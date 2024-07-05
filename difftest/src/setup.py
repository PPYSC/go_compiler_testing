from tree_sitter import Language

Language.build_library(
  # Store the library in the `build` directory
  '/home/shareduser/ysc/difftest/src/resources/build/my-languages.so',

  # Include one or more languages
  [
      '/home/shareduser/ysc/difftest/src/resources/tree-sitter-go-master'
  ]
)
