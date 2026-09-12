# Deploy one model using the portal

1. Open the independently supplied Foundry project; record subscription, resource group, account and project.
2. In the management/quota view, filter the exact model, version, region and deployment type. Record available TPM and required classroom concurrency. A model appearing in the catalogue does not prove quota.
3. Review `deployment-options.yaml` with the instructor. Stop if the available type violates the approved processing geography.
4. Choose Deploy model / base model, select the verified model/version, and name it `acme-lab02-chat-<your-unique-suffix>`. Use the smallest suitable quota allocation; record this name in `data/my-deployment.txt`.
5. Select the approved deployment type and quota, create, and wait until provisioning succeeds. A second attempt should reuse this same deployment rather than create another.
6. Test a synthetic greeting in the playground. Copy its deployment name to MODEL_DEPLOYMENT in this lab's .env. Run `python src/main.py` and `python validate.py --live`.
7. Capture deployment name, model version, type, region and quota in your notes. Explain which fact determines processing geography.
8. Cleanup: select only the deployment recorded in `data/my-deployment.txt` and delete it. Recheck the list. If it is absent, cleanup is already complete. Do not delete the account or instructor's models.

If quota is unavailable, use the instructor's existing approved deployment and label this exercise inspection-only; do not claim you provisioned one.
