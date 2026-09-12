"""Print the owned-resource cleanup instruction; never delete shared Azure resources."""
print("Review rg-<your-environment>: tags must identify this workshop; it must contain no shared resources.")
print("Only then run azd down from this lab's selected disposable environment. This script does not run deletion.")
