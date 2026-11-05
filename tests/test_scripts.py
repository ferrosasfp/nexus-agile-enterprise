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

    def test_listas_y_rangos_de_acs(self):
        # Primera HU de un proyecto nuevo: "AC-1, 2, 3" contaba solo AC-1 y daba 7 falsos "no aparece".
        (self.hu / "work-item.md").write_text("AC-1: a\nAC-2: b\nAC-3: c\nAC-4: d\nAC-5: e\n")
        out = self.story(self.BUENO.replace("- W1 cubre AC-1 y AC-2", "- W1 cubre AC-1, 2, 3 y AC-4..5")
                         .replace("- AC-1 y AC-2: test/a.test.ts", "- ACs 1 a 5: test/a.test.ts"))
        self.assertEqual(out.returncode, 0, out.stdout)

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


class CheckContractMonorepo(unittest.TestCase):
    """Falsos de la segunda HU real: titulo numerado del contrato en el SDD y rutas relativas a apps/web/."""

    def test_sdd_numerado_y_rutas_relativas_a_un_subdirectorio(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        (tmp / "apps/web/components").mkdir(parents=True)
        (tmp / "apps/web/components/a.tsx").write_text("x")
        hu = tmp / "hu"
        hu.mkdir()
        (hu / "work-item.md").write_text("- AC-1: uno\n- AC-2: (eliminado; la persona, en F1). Sale del alcance.\n")
        (hu / "sdd.md").write_text("# SDD\n## 13. Contrato de implementacion\nRutas relativas a `apps/web/`.\n- W1 cubre AC-1\n"
                                   "### Files to Modify/Create\n| Archivo | Accion |\n|---|---|\n| `components/a.tsx` | Modificar |\n"
                                   "### Tests\n- AC-1: t\n")
        out = run("check_contract.py", hu, "--code-root", tmp)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("1 rutas revisadas", out.stdout)
        (hu / "sdd.md").write_text((hu / "sdd.md").read_text().replace("components/a.tsx", "components/zzz.tsx"))
        out = run("check_contract.py", hu, "--code-root", tmp)
        self.assertEqual(out.returncode, 1)
        self.assertIn("zzz.tsx, que no existe", out.stdout)


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


class NexusMemory(unittest.TestCase):
    """Hechos atados al blob SHA de git: vigentes si el archivo no cambio, invalidos si cambio."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        subprocess.run(["git", "init", "-q", str(self.tmp)], check=True)
        (self.tmp / "vitest.config.ts").write_text("export default { test: { include: ['tests/**'] } }\n")
        (self.tmp / "b.ts").write_text("x\n")

    def test_hecho_y_vigencia(self):
        out = run("nexus_memory.py", "hecho", "--repo", self.tmp, "--file", "vitest.config.ts", "--file", "b.ts",
                  "--claim", "vitest incluye tests/**", "--evidence", "vitest.config.ts:1", "--source", "HU-1, 2026-11-04")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("topic_key: hecho/vitest.config.ts+1#vitest-incluye-tests", out.stdout)
        verify = out.stdout.split("Verify: nexus_memory.py vigente --repo <CODE_ROOT> ")[1].split()
        pairs = [verify[i + 1] for i in range(0, len(verify), 2)]
        check = lambda: run("nexus_memory.py", "vigente", "--repo", self.tmp, *sum((["--pair", p] for p in pairs), []))
        self.assertEqual(check().returncode, 0)
        (self.tmp / "b.ts").write_text("y\n")
        changed = check()
        self.assertEqual(changed.returncode, 1)
        self.assertIn("b.ts", changed.stdout)

    def test_dos_hechos_del_mismo_archivo_no_se_pisan(self):
        keys = set()
        for claim in ("el include cubre tests", "el entorno es node"):
            out = run("nexus_memory.py", "hecho", "--repo", self.tmp, "--file", "vitest.config.ts", "--claim", claim, "--evidence", "x", "--source", "x")
            keys.add(out.stdout.splitlines()[0])
        self.assertEqual(len(keys), 2)

    def test_no_guarda_hechos_de_archivos_que_no_existen(self):
        out = run("nexus_memory.py", "hecho", "--repo", self.tmp, "--file", "no-existe.ts", "--claim", "x", "--evidence", "x", "--source", "x")
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()
