/** @type { import("eslint").Linter.Config } */
module.exports = {
  root: true,
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:svelte/recommended",
    "prettier",
  ],
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "prettier"],
  parserOptions: {
    sourceType: "module",
    ecmaVersion: 2020,
    extraFileExtensions: [".svelte"],
  },
  env: {
    browser: true,
    es2017: true,
    node: true,
  },
  overrides: [
    {
      files: ["*.svelte"],
      parser: "svelte-eslint-parser",
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
    },
  ],
  rules: {
    "prettier/prettier": [
      "error",
      {
        plugins: ["prettier-plugin-tailwindcss", "prettier-plugin-svelte"],
        printWidth: 160,
        useTabs: true,
        tabWidth: 4,
        trailingComma: "all",
        singleQuote: true,
        semi: true,
        importOrder: [
          "<THIRD_PARTY_MODULES>",
          "^@/(.*)$",
          "^$env/(.*)$",
          "^[./]",
        ],
        importOrderSeparation: true,
        importOrderSortSpecifiers: true,
        overrides: [{ files: "*.svelte", options: { parser: "svelte" } }],
      },
    ],
  },
};
