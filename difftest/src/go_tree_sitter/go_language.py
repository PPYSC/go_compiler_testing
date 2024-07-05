from tree_sitter import Language


class GoLanguage:
    PATH = "/home/shareduser/ysc/go_compiler_testing/difftest/src/resources/build/my-languages.so"

    language = Language(PATH, "go")

    @staticmethod
    def use_query(query, node):
        return GoLanguage.language.query(query).captures(node)
