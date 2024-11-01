import random
import subprocess

from discriminator.run import Cluster
from generator.node_mask_codet5p import NodeMaskCodet5p
from go_tree_sitter.go_tree_sitter_tool import GoTreeSitterTool
from go_tree_sitter.go_parser import GoParser


import warnings
warnings.filterwarnings("ignore")


class MaskedGoReward:
    def __init__(self):
        self.generator = NodeMaskCodet5p()
        self.discriminator = Cluster()
        self.parser = GoParser()

    def _has_syntax_error(self, code):
        with open("temp.go", "w") as f:
            f.write(code)
        try:
            result = subprocess.run(["go", "vet", "temp.go"], capture_output=True, text=True)
            if result.returncode != 0:
                return True
            else:
                return False
        finally:
            subprocess.run(["rm", "temp.go"])

    def _mask(self, code, mask):
        def find_ith_node(node, index, i):
            if index[0] == i:
                return node
            index[0] += 1
            for child in node.children:
                result = find_ith_node(child, index, i)
                if result is not None:
                    return result
            return None
        
        tree = self.parser.parse(code)
        root_node = tree.root_node

        index = [0]
        target_node = find_ith_node(root_node, index, mask)
        if target_node is not None:
            start_byte = target_node.start_byte
            end_byte = target_node.end_byte
            masked_code = code[:start_byte] + "<mask>" + code[end_byte:]
        else:
            masked_code = code + "<mask>"
        return masked_code

    def _generate(self, masked_code):
        return self.generator.generate(masked_code)
    
    def get_prob(self, code):
        if self._has_syntax_error(code):
            return -10, 10
        else:
            label, probability = self.discriminator.cluster(code)
            prob0 = (probability[1] + 10) / 20
            prob1 = (probability[0] + 10) / 20
            return prob0, prob1

    def get_code_prob(self, code, mask):
        masked_code = self._mask(code, mask)
        new_code = masked_code.replace("<mask>", self._generate(masked_code))
        prob0, prob1 = self.get_prob(new_code)
        
        return new_code, prob0, prob1
