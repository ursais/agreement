# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.modules.module import get_module_resource
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools.convert import convert_file

DEMO_FILES = (
    ("agreement", "demo/demo.xml"),
    ("agreement_legal", "demo/agreement_subtype.xml"),
    ("agreement_legal", "demo/agreement.xml"),
    ("agreement_legal", "demo/agreement_recital.xml"),
    ("agreement_legal", "demo/agreement_section.xml"),
    ("agreement_legal", "demo/agreement_clause.xml"),
    ("agreement_legal", "demo/agreement_appendix.xml"),
    ("agreement_legal", "demo/agreement_line.xml"),
)


@tagged("post_install", "-at_install")
class TestAgreementLegalDemoData(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ensure_demo_loaded()

    @classmethod
    def _ensure_demo_loaded(cls):
        if cls.env.ref("agreement_legal.agreement_recital_market1_witnesseth", False):
            return
        for module, path in DEMO_FILES:
            convert_file(
                cls.env,
                module,
                get_module_resource(module, path),
                idref={},
                mode="init",
                noupdate=True,
                kind="demo",
            )

    def test_demo_agreements_exist(self):
        for xml_id in (
            "market1",
            "market2",
            "market3",
            "market4",
            "market5",
            "market6",
        ):
            agreement = self.env.ref(f"agreement.{xml_id}")
            self.assertTrue(agreement.exists())
            self.assertTrue(agreement.name)
            self.assertTrue(agreement.code)
            self.assertTrue(agreement.partner_id)

    def test_demo_agreements_kanban_fields(self):
        active_agreement = self.env.ref("agreement.market1")
        self.assertEqual(
            active_agreement.stage_id,
            self.env.ref("agreement_legal.agreement_stage_active"),
        )
        self.assertEqual(active_agreement.state, "active")
        self.assertEqual(active_agreement.color, 1)
        self.assertTrue(active_agreement.assigned_user_id)

        template = self.env.ref("agreement.market6")
        self.assertTrue(template.is_template)
        self.assertEqual(template.color, 0)

    def test_demo_agreements_stages_are_distinct(self):
        agreements = self.env["agreement"].browse(
            [self.env.ref(f"agreement.market{index}").id for index in range(1, 6)]
        )
        stages = agreements.mapped("stage_id")
        self.assertGreaterEqual(len(stages), 4)

    def test_demo_agreement_subtypes(self):
        subtype = self.env.ref("agreement_legal.agreement_subtype_contract_support")
        self.assertEqual(
            subtype.agreement_type_id,
            self.env.ref("agreement_legal.agreement_type_contract"),
        )
        agreement = self.env.ref("agreement.market2")
        self.assertEqual(agreement.agreement_subtype_id, subtype)

    def test_demo_agreement_types_on_records(self):
        expectations = {
            "market1": "agreement_legal.agreement_type_agreement",
            "market2": "agreement_legal.agreement_type_contract",
            "market3": "agreement_legal.agreement_type_loi",
            "market4": "agreement_legal.agreement_type_loi",
            "market5": "agreement_legal.agreement_type_agreement",
            "market6": "agreement_legal.agreement_type_contract",
        }
        for xml_id, type_xml_id in expectations.items():
            agreement = self.env.ref(f"agreement.{xml_id}")
            self.assertEqual(
                agreement.agreement_type_id,
                self.env.ref(type_xml_id),
            )

    def test_demo_recitals(self):
        recital = self.env.ref("agreement_legal.agreement_recital_market1_witnesseth")
        agreement = self.env.ref("agreement.market1")
        self.assertEqual(recital.agreement_id, agreement)
        self.assertTrue(recital.content)
        self.assertIn(agreement.code, recital.dynamic_content)

    def test_demo_sections(self):
        section = self.env.ref("agreement_legal.agreement_section_market1_scope")
        agreement = self.env.ref("agreement.market1")
        self.assertEqual(section.agreement_id, agreement)
        self.assertTrue(section.content)
        self.assertIn(agreement.name, section.dynamic_content)

    def test_demo_clauses(self):
        clause = self.env.ref("agreement_legal.agreement_clause_market1_scope_delivery")
        section = self.env.ref("agreement_legal.agreement_section_market1_scope")
        agreement = self.env.ref("agreement.market1")
        self.assertEqual(clause.agreement_id, agreement)
        self.assertEqual(clause.section_id, section)
        self.assertTrue(clause.content)

    def test_demo_appendices(self):
        appendix = self.env.ref("agreement_legal.agreement_appendix_market1_specs")
        agreement = self.env.ref("agreement.market1")
        self.assertEqual(appendix.agreement_id, agreement)
        self.assertTrue(appendix.title)
        self.assertIn(agreement.code, appendix.dynamic_content)

    def test_demo_lines(self):
        line = self.env.ref("agreement_legal.agreement_line_market1_server")
        agreement = self.env.ref("agreement.market1")
        self.assertEqual(line.agreement_id, agreement)
        self.assertTrue(line.product_id)
        self.assertEqual(line.qty, 2)
        self.assertTrue(line.uom_id)

    def test_demo_template_has_content(self):
        template = self.env.ref("agreement.market6")
        self.assertTrue(template.recital_ids)
        self.assertTrue(template.sections_ids)
        self.assertTrue(template.clauses_ids)
        self.assertTrue(template.appendix_ids)
