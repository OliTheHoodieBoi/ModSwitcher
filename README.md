# Minecraft mod switcher

Mod switcher automatically changes the mods in the mods folder when you launch the game.

## Profiles

A "mod profile" is a folder in `.minecraft/mods/profiles` that contains a set of mods that are to be used with a certain profile from the Minecraft launcher. When a mod profile is launched all mods currently in the mods folder will be moved back to their corresponding mod profile folder and all mods in the launched mod profile folder will be moved into the mods folder.

## Config

Mod switcher can optionally be configured by creating/editing the file `modswitcher.json` in the profiles folder.

### Behaviour without config

When Minecraft is started the launcher profile name will be matched against a folder in the profiles directory. If there is no folder with the same name as the launcher profile the `default` profile will be launched instead.

### Behaviour with config

When Minecraft is started the launcher profile name will be attempted to be matched against the [regex](https://en.wikipedia.org/wiki/Regular_expression) **keys** of the profiles object starting from the top. If a match is found of the **value** of the pair is used as the profile to be launched. If no match is found the `default` profile is launched.

### Example configuration

When the launcher profile `Fabric 1.20.4` is started from the Minecraft launcher all the mods will be moved out of the `mods` folder and back to their mod profile folder and mods in the `profiles/Fabric 1.20` folder will be moved to the `mods` folder. Note that the periods (`.`) are escaped with a backslash (`\`) because `Fabric 1\.20.\.4` is a regex and in regex `.` matches any character, not just periods (`.`).

```json
{
  profiles: {
    "Fabric 1\.20\.4": "Fabric 1.20",
    "Vanilla+": "VanillaPlus"
  }
}
```
