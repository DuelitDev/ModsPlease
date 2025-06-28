# Mods, Please
Tool for encrypt/decrypt `Papers, Please` game assets.

# Milestones
| issues                       | O/X |
|------------------------------|:---:|
| **modding streaming assets** |  O  |
| **modding Unity asset file** |  O  |
| **analyze Art.dat**          |  O  |

# How to use
## For v1.4.11
You need to extract Art.dat from Unity assets.
(Try to use UABE)

```shell
# examples
# python packer.py --help
# python packer.py --version
# python packer.py pack [asset_dir_in] [art_file_out]
# python packer.py unpack [art_file_in] [asset_dir_out]

python packer.py --help
python packer.py pack ./output ./Art.dat
python packer.py unpack ./Art.dat ./output
```

## For v1.2.76
```shell
# # NOTE:
# Data must be a MULTIPLE OF 8 BYTES.
# Otherwise the packer will generate invalid game data.
#
# # examples
# python packer.py [mode] [input] [output]
#
# # modes
# decrypt: `-d`
# encrypt: `-e`

# # decrypt
python packer.py -d ./Art.dat ./output # <-- Folder where extracted game data is saved.
#                   ^^^^^^^^^~~ Extracts game data from this file.

# # encrypt
python packer.py -e ./output ./Art.dat # <-- The path where game data is created.
#                   ^^^^^^^^~~ Creates game data with the assets in this folder.
```
