# Minecraft mod switcher

Mod switcher automatically changes your Minecraft mods folder between different profiles when you launch the game.

## Config

The mod switcher is configured in the `modswitcher.json` file in the profiles folder that is automatically created the first time you run the program.

When Minecraft is started the launcher profile name will be attempted to be matched against the **keys** of the profiles object starting from the top. Keys should be a [regex](https://en.wikipedia.org/wiki/Regular_expression). When a match is found of the **value** of the item is the folder in the profiles directory that mods will be moved from.

### Example config

When the profile `Fabric 1.19.4` is started from the Minecraft launcher mods will be moved out of the `mods` folder to the profile that they came from and mods in the `profiles/Fabric` folder will be moved to the `mods` folder.

```json
{
  profiles: {
    "Fabric 1\.19\.4": "Fabric"
  }
}
```
