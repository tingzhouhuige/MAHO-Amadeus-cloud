import config from './config.json'

type RoleKey = keyof typeof config.roles

function normalizeRole(role?: string): RoleKey {
  const value = (role || config.selectedRole || 'maho').trim().toLowerCase()
  return value in config.roles ? value as RoleKey : 'maho'
}

const selectedRole = normalizeRole(import.meta.env.VITE_MAHO_ROLE)
const roleConfig = config.roles[selectedRole]

export const runtimeConfig = {
  ip: config.ip,
  selectedRole,
  amadeusName: roleConfig.amadeusName,
  modelPath: roleConfig.modelPath,
}
