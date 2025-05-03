# paperless-exporter

[![PyPI version](https://img.shields.io/pypi/v/paperless-exporter)](https://pypi.org/project/paperless-exporter/)

Export from Mariner Paperless (gone out of business)

![CLI recording](https://github.com/user-attachments/assets/df400f05-2e22-4ba6-8be3-757ac782d6c2)

to:

- [Obsidian](https://obsidian.md/)-compatible Markdown. See:
  ![paperless](https://github.com/user-attachments/assets/25a937fd-e87c-42b5-9cac-9c8b52cad7b3)
  becomes
  ![obsidian graph](https://github.com/user-attachments/assets/76699715-7fd4-4aa1-8308-eeccf1b4dd25)
  and
  ![obsidian document](https://github.com/user-attachments/assets/7a6c7b0b-de43-4331-96ca-ae999ecc2927)

- Others? Pull requests welcome

## Features

- Document export (library document and original document, fallback to thumbnail)
- Collection support
- Tags support
- Category support

## Limitations

- Your library is NOT encrypted. If it is encrypted you need to remove
  the encryption with your password through the app first.
- This exports only a subset of all fields.

## Command Line Usage

After installing the package, you can use the CLI to export your Paperless library:

```sh
paperless-exporter <path-to-paperless-library> <output-folder>
```

- `<path-to-paperless-library>`: Path to your Paperless library directory
  (must end in `.paperless` and contain `DocumentWallet.documentwalletsql`).
- `<output-folder>`: Path to an empty directory where the
  Obsidian-compatible Markdown library will be generated.

Example:

```sh
paperless-exporter ~/Documents/library.paperless ~/Documents/obsidian-library
```

If the output folder does not exist, it will be created.
If it exists, it must be empty.

### Additional Options

- `--check-orphans`: Check for orphaned files in the Paperless library
  (files that exist in the Documents directory but are not referenced by any receipt).
  This option can be used without specifying an output folder.

Run `paperless-exporter --help` for more information.

## Final Disclaimer

Feel free to use or improve this, but you do so at your own risk.
I'm not responsible for any data loss or other issues caused by the
use of this code and I am in no way affiliated with Mariner Software/Paperless.

## Attribution

An initial version was forked from [Geekfish/paperless-exporter](https://github.com/Geekfish/paperless-exporter)
and used as a base for this source code.

## Similar projects

- [paperless-to-paperless-ngx](https://github.com/jcjones/paperless-to-paperless-ngx)
