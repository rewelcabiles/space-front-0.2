export const computeModuleLoadout = ({
  moduleCatalog,
  primaryModuleName,
  maxModuleSpace = 12,
}) => {
  const installedModuleNames = primaryModuleName ? [primaryModuleName] : [];
  const installedModules = installedModuleNames
    .map((name) => ({ name, definition: moduleCatalog[name] }))
    .filter((entry) => Boolean(entry.definition));

  const modifierTotals = installedModules.reduce((totals, entry) => {
    const modifies = entry.definition.modifies ?? {};
    Object.entries(modifies).forEach(([key, value]) => {
      totals[key] = (totals[key] ?? 0) + Number(value || 0);
    });
    return totals;
  }, {});

  const moduleSpaceUsed = installedModules.reduce(
    (sum, entry) => sum + Number(entry.definition.module_space_requirement ?? 0),
    0,
  );

  const primaryWeapon = installedModules.find(
    (entry) => entry.definition.type === "projectile_weapon",
  );

  return {
    installedModules,
    moduleSpaceUsed,
    maxModuleSpace,
    modifierTotals,
    maxHealth: 100 + Number(modifierTotals.max_hp ?? 0),
    weapon: primaryWeapon?.definition?.type_data ?? null,
  };
};
