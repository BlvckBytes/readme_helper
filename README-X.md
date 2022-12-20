# readme_helper

A small markdown preprocessor which tries to compensate for the lack of features github markdown has been suffering from for the last few years.

<!-- #toc -->

## How It Works

The input markdown file is read bottom to top and command instructions are processed one line at a time, where each command may modify the file by either just removing it's instruction comment or by substituting it with it's own content. After the head of the document is reached, the resulting lines will be written at the output location.

### Configuration

Each command can specify it's configuration keys which can be set within the file using the configuration command. The command invoker will update the the configuration table whenever encountering these instructions, so they may be placed in the order they need to be evaluated to, bottom up.

```markdown
<!-- #configure <command> <key> <value> -->
```

### Table Of Contents

A table of contents headline can be created using the toc command, which will generate a list and possibly indented sublists for all available headlines in the document, while ignoring the root headline.

```markdown
<!-- #toc -->
```

| Configuration Key | Default Value     | Description     |
|-------------------|-------------------|-----------------|
| HEADLINE          | Table Of Contents | Headline of TOC |

### Including Source

A sourcecode file can be included into the document by a reference to it's path in order to avoid the contents getting out of sync, like they often do when statically pasted. The content will be wrapped in a code block with the same language type of the file extension. Configuration keys may dictate how the content is modified before it's substituted for the instruction comment.

```markdown
<!-- #include <path> -->
```

| Configuration Key     | Default Value     | Description                      |
|-----------------------|-------------------|----------------------------------|
| SKIP_LEADING_COMMENTS | false | Whether to skip leading comments             |
| SKIP_LEADING_EMPTY    | false | Whether to skip leading whitespace           |
| SKIP_LEADING_PACKAGE  | false | Whether to skip leading package declarations |
| SKIP_LEADING_IMPORTS  | false | Whether to skip leading import statements    |