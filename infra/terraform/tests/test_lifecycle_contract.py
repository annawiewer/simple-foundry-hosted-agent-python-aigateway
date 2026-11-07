import unittest

from check_contracts import ROOT, check_lifecycle_masks


def resource(mask, name="storage"):
    return (
        f'resource "azapi_resource" "{name}" {{\n'
        f"  lifecycle {{\n    ignore_changes = {mask}\n  }}\n"
        "}\n"
    )


class LifecycleContractTests(unittest.TestCase):
    path = ROOT / "modules" / "foundry-agents" / "main.tf"

    def test_permits_only_the_service_owned_storage_field(self):
        for mask in (
            "[body.properties.networkAcls.resourceAccessRules]",
            "[\nbody.properties.networkAcls.resourceAccessRules,\n]",
        ):
            with self.subTest(mask=mask):
                check_lifecycle_masks(self.path, resource(mask))

    def test_rejects_broader_or_additional_ignored_fields(self):
        for mask in (
            "all",
            "[body]",
            "[body.properties]",
            "[body.properties.networkAcls]",
            "[body.properties.networkAcls.defaultAction]",
            "[body.properties.networkAcls.resourceAccessRules, body.properties.networkAcls]",
        ):
            with self.subTest(mask=mask), self.assertRaisesRegex(
                AssertionError, "broad lifecycle masking forbidden"
            ):
                check_lifecycle_masks(self.path, resource(mask))

    def test_rejects_the_same_field_on_another_owner(self):
        mask = "[body.properties.networkAcls.resourceAccessRules]"
        for path, name in (
            (self.path, "other_storage"),
            (ROOT / "modules" / "ai-gateway" / "main.tf", "storage"),
            (self.path.with_name("other.tf"), "storage"),
        ):
            with self.subTest(path=path, name=name), self.assertRaises(AssertionError):
                check_lifecycle_masks(path, resource(mask, name))

    def test_approved_mask_does_not_hide_another_mask(self):
        allowed = resource("[body.properties.networkAcls.resourceAccessRules]")
        for extra in (resource("[body]", "another"), allowed):
            with self.subTest(extra=extra), self.assertRaises(AssertionError):
                check_lifecycle_masks(self.path, allowed + extra)


if __name__ == "__main__":
    unittest.main()
