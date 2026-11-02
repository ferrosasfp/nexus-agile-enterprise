#!/usr/bin/env python3
"""Pruebas de check_contract.py y check_spec_ids.py. Incluye los dos falsos resultados de la prueba real."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / ".claude/skills/nexus-agile/scripts"


def run(script, *args):
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True)


class CheckContract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.hu = self.tmp / "hu"
        self.hu.mkdir()
        (self.tmp / "src").mkdir()
        (self.tmp / "src/a.ts").write_text("x")
        (self.hu / "work-item.md").write_text("AC-1: uno\nAC-2: dos\n")

    def story(self, text):
        (self.hu / "story-file.md").write_text(text)
        return run("check_contract.py", self.hu, "--code-root", self.tmp)

    BUENO = """# Story
## 2. Waves
- W1 cubre AC-1 y AC-2
## 3. Files to Modify/Create
| Archivo | Accion |
|---|---|
| `src/a.ts` | Modificar (**Excepcion**: solo el import) |
| `src/b.ts` | Crear |
## 7. Tests
### T1
- AC-1 y AC-2: test/a.test.ts
"""

    def test_contrato_bueno_con_titulos_numerados(self):
        # Falso negativo real: con "## 7. Tests" decia que no habia seccion de tests.
        out = self.story(self.BUENO)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("1 rutas revisadas", out.stdout)

    def test_ac_sin_test(self):
        out = self.story(self.BUENO.replace("AC-1 y AC-2: test", "AC-1: test"))
        self.assertEqual(out.returncode, 1)
        self.assertIn("AC-2 no tiene test", out.stdout)

    def test_ruta_que_no_existe(self):
        out = self.story(self.BUENO.replace("`src/a.ts`", "`src/zzz.ts`"))
        self.assertEqual(out.returncode, 1)
        self.assertIn("src/zzz.ts, que no existe", out.stdout)

    def test_no_pasa_en_silencio_sin_rutas(self):
        # Pase silencioso real: si no encontraba la seccion de archivos, daba verde sin revisar nada.
        out = self.story(self.BUENO.replace("## 3. Files to Modify/Create", "## 3. Archivos"))
        self.assertEqual(out.returncode, 1)
        self.assertIn("no pude revisar rutas", out.stdout)

    def test_contrato_unificado_en_el_sdd(self):
        (self.hu / "sdd.md").write_text("# SDD\n## Diseno\nx\n## Contrato de implementacion\n" + self.BUENO.split("\n", 1)[1])
        out = run("check_contract.py", self.hu, "--code-root", self.tmp)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("Contrato de implementacion", out.stdout)


class CheckSpecIds(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def files(self, before, after, sdd):
        for name, text in (("antes.md", before), ("despues.md", after), ("sdd.md", sdd)):
            (self.tmp / name).write_text(text)
        return run("check_spec_ids.py", self.tmp / "antes.md", self.tmp / "despues.md", self.tmp / "sdd.md")

    def test_fusion_correcta(self):
        out = self.files("## REQ-A\n## REQ-B\n", "## REQ-A\n## REQ-C\n", "## ADDED REQ-C\n## REMOVED REQ-B\n")
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_requisito_perdido_en_silencio(self):
        out = self.files("## REQ-A\n## REQ-B\n", "## REQ-A\n", "## ADDED REQ-X\n")
        self.assertEqual(out.returncode, 1)
        self.assertIn("falta REQ-B", out.stdout)


if __name__ == "__main__":
    unittest.main()
