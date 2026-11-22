#!/usr/bin/env python3
"""Pruebas de check_contract.py y check_spec_ids.py. Incluye los dos falsos resultados de la prueba real."""
import json
import os
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

    def test_ac_con_sufijo(self):
        # HU-2 de Nexus Control: AC-8b no se reconocia.
        (self.hu / "work-item.md").write_text("AC-1: a\nAC-2: b\nAC-8b: c\n")
        out = self.story(self.BUENO.replace("- W1 cubre AC-1 y AC-2", "- W1 cubre AC-1, AC-2 y AC-8b").replace("- AC-1 y AC-2: test/a.test.ts", "- AC-1, AC-2 y AC-8b: test/a.test.ts"))
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("3 ACs", out.stdout)

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


class NexusSeed(unittest.TestCase):
    """Siembra retroactiva: candidatas de auto-blindaje y de las secciones de lecciones, sin escribir en la memoria."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.sdd = self.tmp / "doc/sdd"
        for hu in ("001-a", "002-b"):
            (self.sdd / hu).mkdir(parents=True)
        (self.sdd / "001-a/auto-blindaje.md").write_text(
            "# Auto-Blindaje\n\n### [2026-10-29 09:55] Wave 1 — jsdom descarta env() del style\n"
            "- **Error**: la prueba leia un style vacio.\n- **Causa raíz**: jsdom no reconoce env().\n"
            "- **Aplicar en**: toda prueba que verifique un style con env(): leerlo de renderToStaticMarkup.\n\n"
            "### [2026-10-30 10:00] Wave 2 — sin regla\n- **Causa raiz**: el CI corre en zsh.\n")
        (self.sdd / "002-b/auto-blindaje.md").write_text(
            "### [2026-11-02 08:00] Wave 3 — jsdom descarta env() del style otra vez\n"
            "- **Aplicar en**: toda prueba que verifique un style con env(): leerlo de renderToStaticMarkup.\n")
        (self.sdd / "002-b/report.md").write_text(
            "# Reporte\n\n## 8. Lecciones para próximas HUs\n\n1. **NO usar git stash en F3** — usar git show <base>:<archivo>.\n\n"
            "2. **Re-AR estrecho** — solo verificar el revert.\n\n---\n*pie*\n\n## 9. Otra\n\n1. no es leccion\n")

    def test_candidatas_agrupadas_y_con_origen(self):
        out_md, out_json = self.tmp / "c.md", self.tmp / "c.json"
        result = run("nexus_seed.py", "--sdd", self.sdd, "--out", out_md, "--json", out_json)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("5 candidatas", result.stdout)
        text = out_md.read_text()
        # La regla repetida en dos HUs va primero, agrupada.
        first = text.split("## C001.")[1].split("## C002.")[0]
        self.assertIn("HUs: 2", first)
        self.assertIn("001-a/auto-blindaje.md:3", first)
        self.assertIn("NO usar git stash en F3", text)
        self.assertIn("el CI corre en zsh", text)  # sin "Aplicar en", queda la causa
        self.assertNotIn("no es leccion", text)
        self.assertNotIn("pie", text)
        self.assertEqual(len(json.loads(out_json.read_text())), 4)


    def test_casos_de_la_revision(self):
        """Subtitulo anidado, entradas de nivel 4, titulos que no son entradas, bloque de codigo, regla de varias lineas."""
        hu = self.sdd / "003-c"
        hu.mkdir()
        (hu / "auto-blindaje.md").write_text(
            "### [2026-11-01 10:00] Wave 1 — foo\n- **Aplicar en**: regla uno\n  que sigue en otra linea.\n\n"
            "#### [2026-11-01 11:00] Wave 2 — bar\n- **Aplicar en**: regla de nivel cuatro\n\n"
            "### Recomendaciones del CR\n- **Aplicar en**: no es una entrada\n")
        (hu / "report.md").write_text(
            "# R\n\n## 8. Spinoffs / lecciones\n\n- `TradeDock.tsx:237` bug de backlog\n\n### Lecciones extraídas\n\n"
            "**F0 con MCP Atlassian** conviene antes de leer.\n\n```sh\n# comentario\n```\n\n1. item real\n")
        out_json = self.tmp / "c.json"
        run("nexus_seed.py", "--sdd", self.sdd, "--out", self.tmp / "c.md", "--json", out_json)
        items = [c for g in json.loads(out_json.read_text()) for c in g["items"] if c["hu"] == "003-c"]
        by_title = {c["title"]: c for c in items}
        self.assertIn("regla uno que sigue en otra linea.", by_title["Wave 1 — foo"]["rule"])
        self.assertEqual(by_title["Wave 2 — bar"]["rule"], "regla de nivel cuatro")
        self.assertNotIn("Recomendaciones del CR", by_title)
        self.assertIn("F0 con MCP Atlassian", by_title)
        self.assertIn("item real", by_title)
        self.assertFalse(any("TradeDock" in t for t in by_title))
        self.assertEqual(len(items), len(by_title))  # sin duplicados
        self.assertEqual(by_title["item real"]["source"], "report.md:15")


class NexusBrain(unittest.TestCase):
    """Respaldo de la memoria en un repo propio, con un engram falso: no toca la base real."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        self.store = self.tmp / "store.json"
        self.store.write_text(json.dumps([{"id": 1, "sync_id": "a", "title": "trampa: x", "scope": "global"}]))
        fake = bin_dir / "engram"
        fake.write_text(f"""#!{sys.executable}
import json, sys, time
args = sys.argv[1:]
if args[0] == "export":
    obs = json.load(open({str(self.store)!r}))
    json.dump({{"version": 1, "exported_at": str(time.time()), "sessions": [], "observations": obs[::-1], "prompts": []}}, open(args[1], "w"))
elif args[0] == "import":
    print("Observations: %d imported" % len(json.load(open(args[1]))["observations"]))
""")
        fake.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{bin_dir}:/usr/bin:/bin")
        self.brain = self.tmp / "brain"

    def brain_cmd(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPTS / "nexus_brain.py"), *map(str, args)],
                              capture_output=True, text=True, env=self.env)

    def test_respalda_solo_si_cambio_y_restaura(self):
        first = self.brain_cmd("respaldar", "--dir", self.brain)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("RESPALDADO: 1 memorias", first.stdout)
        self.assertNotIn("exported_at", (self.brain / "memoria.json").read_text())
        self.assertIn("SIN CAMBIOS", self.brain_cmd("respaldar", "--dir", self.brain).stdout)
        self.store.write_text(json.dumps([{"id": 1, "sync_id": "a"}, {"id": 2, "sync_id": "b"}]))
        self.assertIn("RESPALDADO: 2 memorias", self.brain_cmd("respaldar", "--dir", self.brain).stdout)
        log = subprocess.run(["git", "-C", str(self.brain), "log", "--oneline"], capture_output=True, text=True).stdout
        self.assertEqual(len(log.splitlines()), 2)
        restored = self.brain_cmd("restaurar", "--dir", self.brain)
        self.assertIn("2 imported", restored.stdout)

    def test_maquina_nueva_no_pisa_el_respaldo(self):
        self.assertEqual(self.brain_cmd("respaldar", "--dir", self.brain).returncode, 0)
        self.store.write_text("[]")  # base vacia: maquina nueva sin restaurar
        result = self.brain_cmd("respaldar", "--dir", self.brain)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("restaurar", result.stderr)
        self.assertIn("trampa: x", (self.brain / "memoria.json").read_text())
        self.assertIn("RESPALDADO: 0", self.brain_cmd("respaldar", "--dir", self.brain, "--forzar").stdout)

    def test_no_escribe_en_un_repo_que_no_es_de_respaldo(self):
        client = self.tmp / "cliente"
        client.mkdir()
        subprocess.run(["git", "init", "-q", str(client)], check=True)
        (client / "app.py").write_text("x\n")
        (client / ".env.local").write_text("SECRETO=1\n")
        result = self.brain_cmd("respaldar", "--dir", client)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((client / "memoria.json").exists())
        other = self.tmp / "con-cosas"
        other.mkdir()
        (other / "nota.txt").write_text("x")
        self.assertNotEqual(self.brain_cmd("respaldar", "--dir", other).returncode, 0)

    def test_lo_borrado_no_se_respalda(self):
        self.store.write_text(json.dumps([{"id": 1, "sync_id": "a"}, {"id": 2, "sync_id": "b", "deleted_at": "2026-11-21"}]))
        self.assertIn("RESPALDADO: 1 memorias", self.brain_cmd("respaldar", "--dir", self.brain).stdout)
        self.assertNotIn('"b"', (self.brain / "memoria.json").read_text())

    def test_push_sin_confirmar_privado_no_empuja(self):
        self.assertEqual(self.brain_cmd("respaldar", "--dir", self.brain).returncode, 0)
        subprocess.run(["git", "-C", str(self.brain), "remote", "add", "origin", "https://gitlab.com/a/b.git"], check=True)
        result = self.brain_cmd("respaldar", "--dir", self.brain, "--push")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no se empuja", result.stderr)
        self.store.write_text(json.dumps([{"id": 1, "sync_id": "a"}, {"id": 3, "sync_id": "c"}]))
        auto = self.brain_cmd("respaldar", "--dir", self.brain)  # sin --push: avisa y queda local
        self.assertEqual(auto.returncode, 0, auto.stderr)
        self.assertIn("NO EMPUJADO", auto.stderr)
        self.assertIn("RESPALDADO", auto.stdout)

    def test_push_sin_remoto_no_inventa_uno(self):
        result = self.brain_cmd("respaldar", "--dir", self.brain, "--push")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sin remoto", result.stderr)


if __name__ == "__main__":
    unittest.main()
