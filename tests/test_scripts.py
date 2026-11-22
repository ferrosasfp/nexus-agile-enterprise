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

    def g(self, *args):
        return subprocess.run(["git", "-C", str(self.tmp), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                              check=True, capture_output=True, text=True).stdout.strip()

    def facts_table(self, *rows):
        return "## Hechos para la memoria\n\n| Hecho | Archivos | Evidencia |\n|---|---|---|\n" + "".join(f"| {a} | {b} | x |\n" for a, b in rows)

    def test_revision_base_que_se_movio_despues_de_spec_verify(self):
        # M1: main recibio otro merge entre SPEC_VERIFY y DONE; contra main a secas, la cita a.py:10-12 pasaba a 5-7.
        (self.tmp / "a.py").write_text("".join(f"line{i}\n" for i in range(1, 21)))
        main = self.commit_base()
        self.g("branch", "-M", "principal")
        self.g("checkout", "-qb", "hu")
        self.g("checkout", "-q", "principal")
        (self.tmp / "a.py").write_text("".join(f"extra{i}\n" for i in range(5)) + "".join(f"line{i}\n" for i in range(1, 21)))
        self.g("commit", "-qam", "otro PR")
        self.g("checkout", "-q", "hu")
        table = self.facts_table(("las lineas diez a doce", "a.py:10-12"))
        out = self.desde("principal", self.report(table))
        self.assertIn("Evidence: a.py:10-12 (SPEC_VERIFY", out.stdout)
        self.assertIn(f"merge-base de principal", out.stdout)
        with_sha = self.report(f"BASE_SHA: {main}\n" + table, "sdd-verification-2.md")
        out = self.desde("principal", with_sha)
        self.assertIn("BASE_SHA del informe", out.stdout)
        self.assertIn("Evidence: a.py:10-12 (SPEC_VERIFY", out.stdout)

    def test_revision_diff_ilegible_descarta(self):
        # M2: con color.diff=always o el archivo marcado -diff, no habia hunks y el hecho se guardaba sin mover.
        (self.tmp / "b2.py").write_text("".join(f"l{i}\n" for i in range(1, 31)))
        base = self.commit_base()
        (self.tmp / "b2.py").write_text("".join(f"l{i}\n" if i != 15 else "cambio\n" for i in range(1, 31)))
        self.g("config", "color.diff", "always")
        out = self.desde(base, self.report(self.facts_table(("rango que toca la 15", "b2.py:10-20"), ("rango lejos", "b2.py:25-26"))))
        self.assertIn("HECHOS: 1 para guardar, 1 descartados", out.stdout)
        self.assertIn("la HU cambio b2.py:10-20", out.stdout)
        (self.tmp / ".git/info/attributes").write_text("b2.py -diff\n")
        out = self.desde(base, self.report(self.facts_table(("rango lejos", "b2.py:25-26"))))
        self.assertIn("HECHOS: 0 para guardar", out.stdout)  # sin hunks legibles no se puede probar nada

    def test_revision_secciones_terminan_con_su_tabla(self):
        # M3 y m4: una tabla posterior no es de la seccion; un titulo dentro de un bloque de codigo no cuenta.
        base = self.commit_base()
        text = ("```\n## Hechos para la memoria\n| ejemplo | src/x/cli.py:3 | x |\n```\n\n" + self.facts_table(("vitest incluye tests", "vitest.config.ts:1"))
                + "\n**Fuera de la seccion (veredicto)**\n\n| Hallazgo | Archivo | Evidencia |\n|---|---|---|\n| BLQ-1 el handler | b.ts:1 | x |\n")
        out = self.desde(base, self.report(text))
        self.assertIn("HECHOS: 1 para guardar, 0 descartados", out.stdout)
        self.assertNotIn("BLQ-1", out.stdout)
        self.assertNotIn("src/x/cli.py", out.stdout)
        wi = self.tmp / "wi.md"
        wi.write_text("## MEMORIA CONSULTADA\n\n| id | q | estado |\n|---|---|---|\n| (#14) | x | VERIFICADA |\n\n"
                      "**Notas del analista**\n\n| #45 en el tracker | preguntar | VERIFICADA con el PO |\n")
        out = run("nexus_memory.py", "usadas", "--file", wi).stdout
        self.assertIn("RENOVAR (mem_review mark_reviewed): #14\n", out)

    def test_revision_hechos_que_empiezan_igual_no_se_pisan(self):
        # M4: "cinco intentos por minuto" y "por hora" daban la misma clave y uno desaparecia sin contarse.
        base = self.commit_base()
        out = self.desde(base, self.report(self.facts_table(("el limite es de cinco intentos por minuto", "b.ts:1"),
                                                              ("el limite es de cinco intentos por hora", "b.ts:1"))))
        self.assertIn("HECHOS: 2 para guardar", out.stdout)
        keys = [l for l in out.stdout.splitlines() if l.startswith("topic_key:")]
        self.assertEqual(len(set(keys)), 2)

    def test_revision_el_ultimo_informe_manda_y_entra_en_el_tope(self):
        # m5: con 10 hechos en el primero y 1 en el ultimo, el del ultimo quedaba afuera del tope.
        for i in range(10):
            (self.tmp / f"f{i}.py").write_text("x\n")
        base = self.commit_base()
        first = self.report(self.facts_table(*[(f"hecho viejo {i}", f"f{i}.py:1") for i in range(10)]))
        last = self.report(self.facts_table(("hecho del informe final", "b.ts:1")), "sdd-verification-2.md")
        out = self.desde(base, first, last)
        self.assertIn("hecho del informe final", out.stdout.split("DESCARTADOS")[0])
        self.assertIn("pasa el tope de 10", out.stdout)

    def test_revision_pipes_escapados_y_estados_con_adornos(self):
        # m6 y m7: `\|` cortaba la celda; un estado con emoji o backticks desaparecia sin aviso.
        base = self.commit_base()
        out = self.desde(base, self.report(self.facts_table(("a \\| b es la regla", "b.ts:1"))))
        self.assertIn("Claim: a | b es la regla", out.stdout)
        wi = self.tmp / "wi.md"
        wi.write_text("## MEMORIA CONSULTADA\n\n| id | q | estado |\n|---|---|---|\n| (#10) | x | ✅ VERIFICADA |\n"
                      "| (#11) | x | `VIGENTE` |\n| (#13) | a \\| b | VERIFICADA |\n| (#20) | x | lo use igual |\n")
        out = run("nexus_memory.py", "usadas", "--file", wi).stdout
        self.assertIn("RENOVAR (mem_review mark_reviewed): #10 #11 #13", out)
        self.assertIn("SIN CLASIFICAR (estado no reconocido: revisarlas): #20", out)

    def test_usadas_separa_renovar_corregir_y_sin_verificar(self):
        # Formato real de GH-25: ids entre parentesis, varios por fila, trampas del plugin sin id, estado con detalle.
        wi = self.tmp / "work-item.md"
        wi.write_text("# HU\n\n## MEMORIA CONSULTADA\n\nBusquedas: \"leccion\" 10\n\n| id | Que dice | Estado |\n|----|----|----|\n"
                      "| M-1 (#887) | hook | VERIFICADA: `x.jsonl:13` |\n"
                      "| M-2 (#861) | ast | SIN VERIFICAR (F3 lo usa) |\n"
                      "| M-5 (#867, #868) | mutantes | **VIGENTE** por hash |\n"
                      "| M-6 (#900) | vieja | DESCARTADA: el archivo cambio |\n"
                      "| TG-T1 | rtk | Aplica: CD-6 |\n\n## PREGUNTAS\n\n| #999 | no es de la seccion | VERIFICADA |\n")
        other = self.tmp / "cierre.md"
        other.write_text("## MEMORIA CONSULTADA\n\n| id | q | e |\n|---|---|---|\n| (#887) | x | DESCARTADA: ya no |\n| (#861) | x | VERIFICADA |\n")
        out = run("nexus_memory.py", "usadas", "--file", wi)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("RENOVAR (mem_review mark_reviewed): #867 #868 #887", out.stdout)
        self.assertIn("CORREGIR (mismo topic_key): #900", out.stdout)
        self.assertIn("SIN VERIFICAR (no se renuevan): #861", out.stdout)
        self.assertNotIn("#999", out.stdout)
        both = run("nexus_memory.py", "usadas", "--file", wi, "--file", other).stdout
        self.assertIn("CORREGIR (mismo topic_key): #887 #900", both)       # gana lo peor
        self.assertIn("RENOVAR (mem_review mark_reviewed): #861 #867 #868", both)  # verificada despues
        none = self.tmp / "sin.md"
        none.write_text("# nada\n")
        self.assertEqual(run("nexus_memory.py", "usadas", "--file", none).returncode, 1)

    def commit_base(self):
        git = lambda *a: subprocess.run(["git", "-C", str(self.tmp), *a], check=True, capture_output=True)
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        return subprocess.run(["git", "-C", str(self.tmp), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

    def report(self, body, name="sdd-verification.md"):
        path = self.tmp / name
        path.write_text("STATUS: VERIFICADO falsas=0 no_verificables=0 debiles=0\nSDD_SHA256: x\n\n" + body)
        return str(path)

    def desde(self, base, *reports, extra=()):
        return run("nexus_memory.py", "desde-verificacion", "--repo", self.tmp, "--base", base, "--source", "GH-9, 2026-11-22",
                   "--project", "demo", *sum((["--report", r] for r in reports), []), *extra)

    TABLE = ("## Afirmaciones VERDADERAS\n\n| Afirmacion | sdd.md:linea | Evidencia |\n|---|---|---|\n"
             "| la tabla de arriba no cuenta | 12 | b.ts:1 |\n\n"
             "## Hechos para la memoria\n\n| Hecho | Archivos | Evidencia |\n|-------|----------|-----------|\n"
             "| vitest solo incluye `tests/**` | `vitest.config.ts:1` | `sed -n 1p` |\n"
             "| b.ts y vitest van juntos | b.ts:1, vitest.config.ts:1 | lectura |\n"
             "| sin archivo | ninguno | x |\n\n## Controles debiles\n\n| c | d.ts:3 | x |\n")

    def test_desde_verificacion_arma_hechos_de_la_seccion(self):
        base = self.commit_base()
        out = self.desde(base, self.report(self.TABLE))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("HECHOS: 2 para guardar, 1 descartados", out.stdout)
        self.assertIn("title: demo hecho: vitest solo incluye tests/**", out.stdout)
        self.assertIn("topic_key: hecho/vitest.config.ts#vitest-solo-incluye-tests", out.stdout)
        self.assertIn("topic_key: hecho/b.ts+1#b-ts-y-vitest-van", out.stdout)
        self.assertIn("Evidence: vitest.config.ts:1 (SPEC_VERIFY, sdd-verification.md: `sed -n 1p`)", out.stdout)
        self.assertNotIn("la tabla de arriba", out.stdout)
        self.assertNotIn("d.ts", out.stdout)
        self.assertIn("sin archivo: sin archivo:linea", out.stdout)

    def test_desde_verificacion_descarta_lo_que_la_hu_cambio(self):
        base = self.commit_base()
        (self.tmp / "b.ts").write_text("cambiado en F3\n")
        (self.tmp / "nuevo.ts").write_text("x\n")
        second = self.TABLE.replace("| sin archivo | ninguno | x |\n", "| sin archivo | ninguno | x |\n| nuevo | nuevo.ts:1 | x |\n")
        out = self.desde(base, self.report(self.TABLE), self.report(second, "sdd-verification-2.md"))
        self.assertIn("topic_key: hecho/vitest.config.ts#", out.stdout)
        self.assertNotIn("topic_key: hecho/b.ts", out.stdout)
        self.assertIn("la HU cambio b.ts:1-1", out.stdout)
        self.assertIn("nuevo.ts no existia en", out.stdout)

    def test_desde_verificacion_guarda_si_la_hu_no_toco_las_lineas_citadas(self):
        # Caso real: SPEC_VERIFY cita archivos que la HU despues modifica. Si los cambios no tocan las lineas
        # citadas, el hecho vale y la cita pasa a las lineas de hoy.
        (self.tmp / "m.py").write_text("".join(f"linea {i}\n" for i in range(1, 21)))
        base = self.commit_base()
        lines = [f"linea {i}\n" for i in range(1, 21)]
        lines[1:1] = ["nueva a\n", "nueva b\n"]         # inserta 2 antes de la 2
        lines[-1] = "linea 20 cambiada\n"               # cambia la 20
        (self.tmp / "m.py").write_text("".join(lines))
        table = ("## Hechos para la memoria\n\n| Hecho | Archivos | Evidencia |\n|---|---|---|\n"
                 "| el bloque del medio sigue igual | m.py:8-12 | x |\n"
                 "| la ultima linea dice 20 | m.py:20 | x |\n"
                 "| las dos primeras | m.py:1-2 | x |\n")
        out = self.desde(base, self.report(table))
        self.assertIn("HECHOS: 1 para guardar, 2 descartados", out.stdout)
        self.assertIn("Evidence: m.py:10-14 (SPEC_VERIFY", out.stdout)
        self.assertIn("la HU cambio m.py:20-20", out.stdout)
        self.assertIn("la HU cambio m.py:1-2", out.stdout)

    def test_desde_verificacion_sin_seccion_tope_y_base_invalida(self):
        base = self.commit_base()
        out = self.desde(base, self.report("## Afirmaciones VERDADERAS\n\n| a | b.ts:1 | x |\n"))
        self.assertIn("HECHOS: 0", out.stdout)
        self.assertIn("SIN SECCION", out.stdout)
        out = self.desde(base, self.report(self.TABLE), extra=("--max", "1"))
        self.assertIn("HECHOS: 1 para guardar", out.stdout)
        self.assertIn("pasa el tope de 1", out.stdout)
        self.assertNotEqual(self.desde("no-existe", self.report(self.TABLE)).returncode, 0)


class NexusCandidates(unittest.TestCase):
    """Candidatas de una HU: bloqueos del hook, violaciones, BLQ y MAYOR de las revisiones, auto-blindaje."""

    TRAMPAS = SCRIPTS.parent / "references/trampas_globales.md"

    def setUp(self):
        self.hu = Path(tempfile.mkdtemp()) / "025-demo"
        self.hu.mkdir()
        self.addCleanup(shutil.rmtree, self.hu.parent)

    def cands(self, *extra):
        out = run("nexus_candidates.py", "--hu-dir", self.hu, *extra)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def test_junta_las_cuatro_fuentes(self):
        block = {"agent": "nexus-dev", "tool": "Bash", "message": "los gates solo los registra el hook"}
        (self.hu / ".blocks.jsonl").write_text("\n".join(json.dumps({**block, "message": m}) for m in (
            "nexus-dev no puede escribir /a/b/x.ts. Si es un falso positivo, ...",
            "nexus-dev no puede escribir /c/y.ts. Si es un falso positivo, ...")) + "\nno es json\n")
        (self.hu / ".gates.jsonl").write_text(json.dumps({"gate": "HU_APPROVED"}) + "\n" + json.dumps(
            {"gate": "VIOLATION", "by": "nexus-security", "restored": ["/r/security-review.md"], "command": "python3 -"}) + "\n")
        (self.hu / "ar-report.md").write_text("STATUS: RECHAZADO\n\n## BLQ previos\n\n### BLQ-MED-1 · falso OK\n"
                                              "### MNR-1 · menor\n```\n### BLQ-9 dentro de un bloque\n```\n")
        (self.hu / "cr-report.md").write_text("## 2. Error Handling — MAYOR (MAY-1)\n")
        (self.hu / "auto-blindaje.md").write_text("### [2026-11-21 21:40] Wave unica — algo\n- **Aplicar en**: la regla.\n")
        out = self.cands()
        self.assertIn("5 candidatas", out)
        self.assertIn("2 vez/veces, nexus-dev", out)          # los dos bloqueos con rutas distintas son uno
        self.assertIn("(violacion, `.gates.jsonl:2`): nexus-security cambio security-review.md", out)
        self.assertIn("`ar-report.md:5`): BLQ-MED-1", out)
        self.assertIn("MAYOR (MAY-1)", out)
        self.assertIn("(auto-blindaje, `auto-blindaje.md:1`)", out)
        for absent in ("BLQ previos", "MNR-1", "BLQ-9"):
            self.assertNotIn(absent, out)

    def test_marca_la_trampa_global_que_repite(self):
        # Caso real (GH-25): el bloqueo de .gates.jsonl por Bash ya era T2; un BLQ de otro tema no se parece a nada.
        (self.hu / "auto-blindaje.md").write_text(
            "### [2026-11-21 21:40] Wave unica — Comando con `.gates.jsonl` bloqueado por el hook\n"
            "- **Aplicar en**: toda reproduccion que necesite un `.gates.jsonl`: citar el codigo o tests existentes, "
            "o usar un fixture ya construido, y no escribir ese nombre en un comando.\n")
        (self.hu / "ar-report.md").write_text("### BLQ-MED-1 · Cat. 12 · falso OK en la fila Escritura en el proyecto observado\n")
        out = self.cands("--trampas", self.TRAMPAS)
        self.assertEqual(out.count("posible T"), 1)
        self.assertIn("**posible T2**", out)

    def test_hallazgos_en_vinetas_y_tablas(self):
        # m8: solo veia los hallazgos escritos como titulo.
        (self.hu / "ar-report.md").write_text("| id | que |\n|---|---|\n| BLQ-ALTO-1 | sin validar |\n\n"
                                              "- **BLQ-MED-2**: falta el test\n- MNR-1 menor\n")
        out = self.cands()
        self.assertIn("BLQ-ALTO-1 | sin validar", out)
        self.assertIn("BLQ-MED-2: falta el test", out)
        self.assertNotIn("MNR-1", out)
        (self.hu / "ar-report-2.md").write_text("## Estado de los BLQ previos\n\n| BLQ-MED-2 | Resuelto |\n\n### BLQ-BAJO-4 · nuevo\n")
        out = self.cands()
        self.assertEqual(out.count("BLQ-MED-2"), 1)          # la tabla de estado de la re-revision no lo repite
        self.assertIn("`ar-report-2.md:5`): BLQ-BAJO-4", out)
        rel = subprocess.run([sys.executable, "-I", str(SCRIPTS / "nexus_candidates.py"), "--hu-dir", "."],
                             cwd=self.hu, capture_output=True, text=True).stdout
        self.assertIn("# Candidatas a leccion de 025-demo", rel)

    def test_hu_sin_nada(self):
        self.assertIn("Ninguna", self.cands())


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
