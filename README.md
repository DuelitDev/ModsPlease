# Mods, Please
Tool for encrypt/decrypt `Papers, Please` game assets.

# Milestones
| issues                       | O/X |
|------------------------------|:---:|
| **modding streaming assets** |  O  |
| **modding unity asset file** |  O* |
| **analyze Art.dat**          |  X  |

\* Use UABE

# How to use
## For v1.4.x
Work in progress.

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
# encrypt: `-e`
# decrypt: `-d`

# # encrypt
python packer.py -e ./output ./Art.dat # <-- The path where game data is created.
#                   ^^^^^^^^~~ Creates game data with the assets in this folder.

# # decrypt
python packer.py -d ./Art.dat ./output # <-- Folder where extracted game data is saved.
#                   ^^^^^^^^^~~ Extracts game data from this file.
```
