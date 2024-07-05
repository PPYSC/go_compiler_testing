import random

from discriminator.run import Cluster
from generator.node_mask_codet5p import NodeMaskCodet5p
from go_tree_sitter.go_parser import GoParser

import warnings
warnings.filterwarnings("ignore")


class MaskedGoReward:
    def __init__(self):
        self.generator = NodeMaskCodet5p()
        self.discriminator = Cluster()
        self.parser = GoParser()

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
            masked_code= code + "<mask>"
        return masked_code

    def _generate(self, masked_code):
        return self.generator.generate(masked_code)
    
    def _reward_cost(self, code):
        # TODO: compileable
        label, probability = self.discriminator.cluster(code)
        return probability[1], probability[0]

    def get_code_reward(self, code, mask):
        masked_code = self._mask(code, mask)
        print(masked_code)
        new_code = masked_code.replace("<mask>", self._generate(masked_code))
        reward, cost = self._reward_cost(new_code)
        
        return new_code, reward, cost


code = "package main\nfunc helloworld() {\n\tprintln(\"Hello World!\")\n}"

rst = MaskedGoReward().get_code_reward(code,8)
print(rst[0])
print('='*50)
print(rst[1], rst[2])

