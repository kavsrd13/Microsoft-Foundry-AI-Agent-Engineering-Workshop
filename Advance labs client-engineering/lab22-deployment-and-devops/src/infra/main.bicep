targetScope = 'subscription'
param environmentName string
param location string
param apiClientId string
param spaClientId string
param modelName string
param modelVersion string
param modelSku string = 'Standard'
param modelCapacity int = 10
resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: {
    'azd-env-name': environmentName
    purpose: 'resident-workshop'
  }
}
module resources 'resources.bicep' = {
  name: 'workshop-resources'
  scope: rg
  params: {
    location: location
    environmentName: environmentName
    apiClientId: apiClientId
    spaClientId: spaClientId
    modelName: modelName
    modelVersion: modelVersion
    modelSku: modelSku
    modelCapacity: modelCapacity
  }
}
output AZURE_RESOURCE_GROUP string = rg.name
output WEB_APP_NAME string = resources.outputs.webName
output FUNCTION_APP_NAME string = resources.outputs.functionName
output PROJECT_ENDPOINT string = resources.outputs.projectEndpoint
output SEARCH_ENDPOINT string = resources.outputs.searchEndpoint
output COSMOS_ENDPOINT string = resources.outputs.cosmosEndpoint
