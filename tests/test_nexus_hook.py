#!/usr/bin/env python3
"""Pruebas de los hooks con entradas como las de Claude Code. Sin modelo y sin red."""
import json
import time
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "nexus_hook.py"


class HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = self.tmp / "repo"
        self.hu = self.repo / "doc/sdd/001-demo"
        self.hu.mkdir(parents=True)
        self.git("init", "-q")
        self.git("config", "user.email", "a@b.c")
        self.git("config", "user.name", "t")
        (self.repo / "app.ts").write_text("a\n")
        self.git("add", "app.ts")
        self.git("commit", "-qm", "init")
        self.env = dict(os.environ, CLAUDE_PLUGIN_DATA=str(self.tmp / "data"))

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True)

    def run_hook(self, command, **data):
        data.setdefault("session_id", "s1")
        data.setdefault("cwd", str(self.repo))
        return subprocess.run([sys.executable, "-I", str(HOOK), command], input=json.dumps(data),
                              capture_output=True, text=True, env=self.env)

    def spawn(self, phase, agent="nexus-architect"):
        prompt = f"RUTAS: CODE_ROOT={self.repo} · SKILL_DIR=[usa la que exista]\nFASE: {phase}\nHU_DIR: {self.hu}\nPROPIEDAD: propia (archivo, de prueba)\nhaz"
        return self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": agent, "prompt": prompt})

    def type_gate(self, gate):
        return self.run_hook("prompt", prompt=f"{gate} {self.hu}")

    def write(self, name, text="x\n"):
        (self.hu / name).write_text(text)

    def assertBlocked(self, result, reason=""):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(reason, result.stderr)

    def assertAllowed(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)


class Fases(HookCase):
    def test_otro_agente_no_se_toca(self):
        self.assertAllowed(self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": "Explore", "prompt": "x"}))

    def test_sin_fase_bloquea(self):
        result = self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": "nexus-dev", "prompt": "x"})
        self.assertBlocked(result, "FASE")

    def test_nombre_de_plugin_tambien_bloquea(self):
        result = self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": "nexus-agile:nexus-dev", "prompt": "x"})
        self.assertBlocked(result, "FASE")

    def test_plugin_exige_prefijo(self):
        self.env["CLAUDE_PLUGIN_ROOT"] = "/x"
        self.assertBlocked(self.spawn("F1", "nexus-analyst"), "nexus-agile:nexus-analyst")
        self.assertAllowed(self.spawn("F1", "nexus-agile:nexus-analyst"))

    def test_skill_dir_con_plugin(self):
        root = self.tmp / "plugin"
        (root / ".claude/skills/nexus-agile").mkdir(parents=True)
        self.env["CLAUDE_PLUGIN_ROOT"] = str(root)
        launch = lambda skill: self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": "nexus-agile:nexus-analyst",
                                             "prompt": f"RUTAS: CODE_ROOT={self.repo}{skill}\nFASE: F1\nHU_DIR: {self.hu}\nPROPIEDAD: propia (archivo)"})
        for skill in (f" · SKILL_DIR={root}/.claude/skills/nexus-agile", " · SKILL_DIR=${CLAUDE_PLUGIN_ROOT}/.claude/skills/nexus-agile"):
            with self.subTest(skill=skill):
                self.assertAllowed(launch(skill))
        # Defecto real: la version vieja de ~/.claude, el placeholder de la plantilla, o nada
        for skill, reason in ((" · SKILL_DIR=~/.claude/skills/nexus-agile", "fuera del plugin"), (" · SKILL_DIR=[valor]", "sin resolver"),
                              ("", "falta SKILL_DIR"), (f" · SKILL_DIR={root}/../otra/nexus-agile", "fuera del plugin")):
            with self.subTest(skill=skill):
                self.assertBlocked(launch(skill), reason)

    def test_gate_de_propiedad(self):
        # Segunda HU real: se implemento entera una HU asignada a otro integrante.
        launch = lambda line: self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": "nexus-analyst",
                                            "prompt": f"RUTAS: CODE_ROOT={self.repo}\nFASE: F0F1\nHU_DIR: {self.hu}\n{line}"})
        self.assertBlocked(launch(""), "PROPIEDAD")
        self.assertBlocked(launch("PROPIEDAD: [resultado]"), "PROPIEDAD")
        self.assertBlocked(launch("PROPIEDAD: ajena (jira X-1, asignada a otra persona)"), "Escala")
        self.assertBlocked(launch("PROPIEDAD: no se"), "no es propia")
        for line in ("PROPIEDAD: propia (jira X-1, asignada a mi)", "PROPIEDAD: libre (github #4, sin asignar)",
                     "PROPIEDAD: autorizada por la persona (la tomo aunque es de otro)"):
            with self.subTest(line=line):
                self.assertAllowed(launch(line))
        # Con el work-item ya escrito (relanzar al analista con respuestas), no se vuelve a pedir
        self.write("work-item.md")
        self.assertAllowed(launch(""))

    def test_copia_sin_plugin_no_exige_prefijo(self):
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))

    def test_code_root_sin_resolver(self):
        prompt = f"RUTAS: CODE_ROOT=[valor]\nFASE: F1\nHU_DIR: {self.hu}"
        self.assertBlocked(self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": "nexus-analyst", "prompt": prompt}), "sin resolver")

    def test_sin_repo_git_bloquea(self):
        other = self.tmp / "sin-git"
        other.mkdir()
        self.write("work-item.md")
        prompt = f"FASE: F2\nHU_DIR: {self.hu}"
        result = self.run_hook("gate", cwd=str(other), tool_name="Agent", tool_input={"subagent_type": "nexus-architect", "prompt": prompt})
        self.assertBlocked(result, "no es un repo git")

    def test_fase_desconocida(self):
        self.assertBlocked(self.spawn("F9"), "desconocida")

    def test_f1_sin_precondiciones(self):
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))

    def test_f2_sin_artefacto(self):
        self.assertBlocked(self.spawn("F2"), "work-item.md")

    def test_f2_sin_gate(self):
        self.write("work-item.md")
        self.assertBlocked(self.spawn("F2"), "HU_APPROVED")

    def test_pregunta_abierta_frena_f2(self):
        self.write("work-item.md", "# WI\n## PREGUNTAS PARA EL HUMANO\n- [ ] que formato\n")
        self.type_gate("HU_APPROVED")
        self.assertBlocked(self.spawn("F2"), "sin responder")

    def test_pregunta_abierta_frena_f3_en_fast(self):
        self.write("work-item.md", "- Pipeline: FAST\n## PREGUNTAS PARA EL HUMANO\n- [ ] que formato\n")
        self.type_gate("HU_APPROVED")
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "sin responder")

    def test_pregunta_respondida_no_frena(self):
        self.write("work-item.md", "# WI\n## PREGUNTAS PARA EL HUMANO\n- [x] que formato: CSV\n\n## Otra\n- [ ] no es pregunta\n")
        self.type_gate("HU_APPROVED")
        self.assertAllowed(self.spawn("F2"))

    def test_f2_con_gate(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.assertAllowed(self.spawn("F2"))

    def test_gate_guarda_copia_de_lo_aprobado(self):
        self.write("work-item.md", "version uno\n")
        self.type_gate("HU_APPROVED")
        copies = list((self.hu / ".versions").glob("work-item-*.md"))
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0].read_text(), "version uno\n")
        self.assertIn(".versions/", (self.hu / ".gates.jsonl").read_text())

    def test_reaprobar_guarda_otra_copia(self):
        self.write("work-item.md", "uno\n")
        self.type_gate("HU_APPROVED")
        self.write("work-item.md", "dos\n")
        self.type_gate("HU_APPROVED")
        self.assertEqual(len(list((self.hu / ".versions").glob("work-item-*.md"))), 2)

    def test_documento_cambiado_tras_aprobar(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.write("work-item.md", "otro\n")
        self.assertBlocked(self.spawn("F2"), "cambio despues")

    def test_reaprobar_destraba(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.write("work-item.md", "otro\n")
        self.type_gate("HU_APPROVED")
        self.assertAllowed(self.spawn("F2"))

    def test_texto_aproximado_no_es_gate(self):
        self.write("work-item.md")
        self.run_hook("prompt", prompt="dale, HU_APPROVED")
        self.run_hook("prompt", prompt="ok")
        self.assertBlocked(self.spawn("F2"), "HU_APPROVED")

    def verify(self, status="VERIFICADO falsas=0 no_verificables=0", sha=None):
        import hashlib
        digest = sha or hashlib.sha256((self.hu / "sdd.md").read_bytes()).hexdigest()
        self.write("sdd-verification.md", f"STATUS: {status}\nSDD_SHA256: {digest}\n")

    def test_f4_de_launch_no_pide_ar_ni_cr(self):
        # SKILL.md: LAUNCH no tiene AR ni CR; el hook se los pedia en F4.
        self.write("work-item.md", "- Pipeline: LAUNCH\n## PREGUNTAS PARA EL HUMANO\nNinguna\n")
        self.type_gate("HU_APPROVED")
        result = self.spawn("F4", "nexus-qa")
        self.assertNotIn("ar-report", result.stderr)

    def test_f3_quality_exige_verificacion_del_sdd(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md", "## Contrato de implementacion\n")
        self.type_gate("SPEC_APPROVED")
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "sdd-verification.md")
        self.verify("CON_FALSAS falsas=2 no_verificables=0")
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "falsas")
        self.verify(sha="0" * 64)
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "otra version")
        self.verify()
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def security(self, status="APROBADO altos=0 medios=0 notas=1", sha=None):
        import hashlib
        digest = sha or hashlib.sha256((self.hu / "sdd.md").read_bytes()).hexdigest()
        self.write("security-review.md", f"STATUS: {status}\nSDD_SHA256: {digest}\n")

    def test_f3_exige_revision_de_seguridad_si_el_work_item_la_pide(self):
        self.write("work-item.md", "security_review: required\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md", "## Contrato de implementacion\n")
        self.type_gate("SPEC_APPROVED")
        self.verify()
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "security-review.md")
        self.security("CON_HALLAZGOS altos=1 medios=0 notas=0")
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "hallazgos de seguridad abiertos")
        self.security(sha="0" * 64)
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "otra version")
        self.security()
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def test_sin_riesgo_no_hay_revision_de_seguridad(self):
        self.write("work-item.md", "security_review: no\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md", "## Contrato de implementacion\n")
        self.type_gate("SPEC_APPROVED")
        self.verify()
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def test_security_escribe_solo_su_reporte(self):
        self.assertAllowed(self.run_hook("gate", agent_type="nexus-agile:nexus-security", tool_name="Write",
                                         tool_input={"file_path": str(self.hu / "security-review.md")}))
        self.assertBlocked(self.run_hook("gate", agent_type="nexus-agile:nexus-security", tool_name="Write",
                                         tool_input={"file_path": str(self.hu / "sdd.md")}))
        self.assertBlocked(self.run_hook("gate", agent_type="nexus-agile:nexus-security", tool_name="Bash", cwd="/home/x/repo",
                                         tool_input={"command": "echo x > /home/x/repo/a.ts"}))

    def test_spec_verify_se_puede_apagar(self):
        (self.repo / "project-context.md").write_text("| spec_verify | false |\n")
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md", "## Contrato de implementacion\n")
        self.type_gate("SPEC_APPROVED")
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def test_spec_verify_necesita_sdd_y_hu(self):
        self.assertBlocked(self.spawn("SPEC_VERIFY", "nexus-adversary"), "sdd.md")

    def _hasta_spec(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md")
        self.type_gate("SPEC_APPROVED")

    def test_f3_quality_sin_contrato(self):
        # unified es el default: sin campo, el contrato se busca en el SDD.
        self._hasta_spec()
        self.verify()
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "Contrato de implementacion")

    def test_f3_classic_exige_story(self):
        self.write("work-item.md", "contract_mode: classic\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md", "## Contrato de implementacion\n")
        self.type_gate("SPEC_APPROVED")
        self.verify()
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "story-file.md")

    def test_f25_solo_con_classic(self):
        self._hasta_spec()
        self.assertBlocked(self.spawn("F2.5"), "no hay F2.5")
        self.write("work-item.md", "contract_mode: classic\n")
        self.type_gate("HU_APPROVED")
        self.assertAllowed(self.spawn("F2.5"))

    def test_f3_quality_con_story(self):
        self._hasta_spec()
        self.write("story-file.md")
        self.verify()
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def test_f3_unified_exige_seccion(self):
        self.write("work-item.md", "contract_mode: unified\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md")
        self.type_gate("SPEC_APPROVED")
        self.verify()
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "Contrato")

    def test_f3_unified_con_seccion(self):
        self.write("work-item.md", "contract_mode: unified\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md", "## Contrato de implementacion\n")
        self.type_gate("SPEC_APPROVED")
        self.verify()
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def test_f25_con_unified_bloquea(self):
        self.write("work-item.md", "contract_mode: unified\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md")
        self.type_gate("SPEC_APPROVED")
        self.assertBlocked(self.spawn("F2.5"), "no hay F2.5")

    def test_fast_no_pide_spec(self):
        self.write("work-item.md", "- Pipeline: FAST\n")
        self.type_gate("HU_APPROVED")
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def test_pipeline_ausente_es_quality(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "sdd.md")

    def test_f4_con_blq_abierto(self):
        self.write("work-item.md")
        self.write("ar-report.md", "STATUS: RECHAZADO open_blq=2\n")
        self.write("cr-report.md", "STATUS: APROBADO open_blq=0\n")
        self.assertBlocked(self.spawn("F4", "nexus-qa"), "BLOQUEANTEs abiertos")

    def test_f4_lee_el_ultimo_reporte(self):
        self.write("work-item.md")
        self.write("ar-report.md", "STATUS: RECHAZADO open_blq=2\n")
        self.write("ar-report-2.md", "STATUS: APROBADO open_blq=0\n")
        self.write("cr-report.md", "STATUS: APROBADO open_blq=0\n")
        self.assertAllowed(self.spawn("F4", "nexus-qa"))

    def test_f4_sin_status(self):
        self.write("work-item.md")
        self.write("ar-report.md", "todo bien\n")
        self.write("cr-report.md", "STATUS: APROBADO open_blq=0\n")
        self.assertBlocked(self.spawn("F4", "nexus-qa"), "STATUS")

    def test_fast_f4_sin_reportes(self):
        self.write("work-item.md", "pipeline: FAST\n")
        self.assertAllowed(self.spawn("F4", "nexus-qa"))

    def test_done_sin_aprobacion(self):
        self.write("work-item.md")
        self.write("validation.md", "STATUS: RECHAZADO\n")
        self.assertBlocked(self.spawn("DONE", "nexus-docs"), "APROBADO")

    def test_done_aprobado(self):
        self.write("work-item.md")
        self.write("validation.md", "STATUS: APROBADO PARA DONE\n")
        self.assertAllowed(self.spawn("DONE", "nexus-docs"))

    def test_done_exige_release_si_se_declara(self):
        self.write("work-item.md")
        self.write("validation.md", "STATUS: APROBADO PARA DONE\n")
        (self.repo / "project-context.md").write_text("| **release_gate** | true |\n")
        self.assertBlocked(self.spawn("DONE", "nexus-docs"), "RELEASE_APPROVED")


class Delegacion(HookCase):
    def test_auto_delega_hu_y_lo_registra(self):
        self.write("work-item.md")
        self.run_hook("prompt", prompt="/nexus-auto X-1")
        self.assertAllowed(self.spawn("F2"))
        entries = (self.hu / ".gates.jsonl").read_text()
        self.assertIn("claude-delegated", entries)

    def test_auto_en_medio_de_instrucciones(self):
        # Segunda HU real: el comando venia en una linea de un bloque de instrucciones y no delego.
        out = self.run_hook("prompt", prompt="Vamos a probar AUTO.\n\nCOMO CORRER\n- Lanza /nexus-agile:nexus-auto X-1 --supervisor.")
        self.assertIn("delegada", out.stdout)
        self.write("work-item.md")
        # Con --supervisor, el gate delegado necesita su veredicto (clase GateDelegadoRevisado)
        self.assertBlocked(self.spawn("F2"), "supervisor")

    def test_mencionar_auto_no_delega(self):
        self.run_hook("prompt", prompt="La HU anterior uso el comando nexus-auto, explicalo")
        self.write("work-item.md")
        self.assertBlocked(self.spawn("F2"), "al inicio de una linea")

    def test_auto_nunca_delega_release(self):
        self.write("work-item.md")
        self.write("validation.md", "STATUS: APROBADO PARA DONE\n")
        (self.repo / "project-context.md").write_text("release_gate: true\n")
        self.run_hook("prompt", prompt="/nexus-agile:nexus-auto X-1")
        self.assertBlocked(self.spawn("DONE", "nexus-docs"), "RELEASE_APPROVED")

    def test_override_deja_pasar_una_vez_y_queda_registrado(self):
        self.write("work-item.md")
        self.run_hook("prompt", prompt="NEXUS_OVERRIDE gate de otra sesion")
        self.assertAllowed(self.spawn("F2"))
        self.assertIn("gate de otra sesion", (self.hu / ".gates.jsonl").read_text())
        self.assertBlocked(self.spawn("F2"), "HU_APPROVED")

    def test_opcion_de_askuserquestion_registra(self):
        self.write("work-item.md")
        self.spawn("F1", "nexus-analyst")
        self.run_hook("answer", tool_name="AskUserQuestion", tool_response={"answers": {"Apruebas?": "HU_APPROVED"}})
        self.assertAllowed(self.spawn("F2"))

    def test_otra_respuesta_no_registra(self):
        self.write("work-item.md")
        self.spawn("F1", "nexus-analyst")
        self.run_hook("answer", tool_name="AskUserQuestion", tool_response={"answers": {"Apruebas?": "RECHAZAR"}})
        self.assertBlocked(self.spawn("F2"), "HU_APPROVED")


class Escritura(HookCase):
    def write_as(self, agent, path):
        return self.run_hook("gate", agent_type=agent, tool_name="Write", tool_input={"file_path": str(path)})

    def bash_as(self, agent, command):
        return self.run_hook("gate", agent_type=agent, tool_name="Bash", tool_input={"command": command})

    def test_revisor_no_escribe_codigo(self):
        self.assertBlocked(self.write_as("nexus-adversary", self.repo / "app.ts"), "no puede escribir")

    def test_prefijo_de_plugin(self):
        self.assertBlocked(self.write_as("nexus-agile:nexus-adversary", self.repo / "app.ts"), "no puede escribir")

    def test_revisor_escribe_su_reporte(self):
        self.assertAllowed(self.write_as("nexus-adversary", self.hu / "ar-report-2.md"))

    def test_dev_no_escribe_documentos_aprobados_ni_reportes(self):
        # El dev no tenia regla de ruta: podia reescribir el SDD aprobado o el reporte del CR.
        for name in ("sdd.md", "work-item.md", "story-file.md", "cr-report-2.md", "validation.md", "cierre.md", ".versions/sdd-abc.md"):
            self.assertBlocked(self.write_as("nexus-dev", self.hu / name), "nexus-dev no puede escribir")
        # Su codigo, sus notas y el contexto del proyecto, si
        for path in (self.repo / "src/a.py", self.hu / "auto-blindaje.md", self.hu / "implementation-log.md", self.repo / "project-context.md"):
            self.assertAllowed(self.write_as("nexus-dev", path))

    def test_qa_no_escribe_reporte_ajeno(self):
        self.assertBlocked(self.write_as("nexus-qa", self.hu / "ar-report.md"))

    def test_qa_escribe_en_copia_desechable(self):
        self.assertAllowed(self.run_hook("gate", agent_type="nexus-qa", tool_name="Write", cwd="/home/x/repo", tool_input={"file_path": "/tmp/copia/x.ts"}))

    def test_supervisor_no_escribe_nada(self):
        self.assertBlocked(self.write_as("nexus-supervisor", self.hu / "work-item.md"))
        self.assertBlocked(self.bash_as("nexus-supervisor", "echo x > notas.md"))

    def test_supervisor_se_lanza_sin_precondiciones(self):
        self.assertAllowed(self.spawn("SUPERVISION", "nexus-supervisor"))

    def test_arquitecto_no_toca_codigo(self):
        self.assertBlocked(self.write_as("nexus-architect", self.repo / "app.ts"))

    def test_dev_escribe_codigo(self):
        self.assertAllowed(self.write_as("nexus-dev", self.repo / "app.ts"))

    def test_sesion_principal_no_se_limita(self):
        self.assertAllowed(self.write_as("", self.repo / "app.ts"))

    def test_nadie_escribe_gates(self):
        self.assertBlocked(self.write_as("nexus-dev", self.hu / ".gates.jsonl"), "gates")
        self.assertBlocked(self.bash_as("nexus-dev", f"echo x >> {self.hu}/.gates.jsonl"), "gates")

    def test_leer_gates_esta_permitido(self):
        for command in (f"cat {self.hu}/.gates.jsonl", f"sha256sum {self.hu}/*.md {self.hu}/.gates.jsonl", f"grep SPEC {self.hu}/.gates.jsonl"):
            with self.subTest(command=command):
                self.assertAllowed(self.bash_as("nexus-supervisor", command))
        self.assertBlocked(self.bash_as("nexus-dev", f"sed -i d {self.hu}/.gates.jsonl"), "gates")
        self.assertBlocked(self.bash_as("", f"rm {self.hu}/.gates.jsonl"), "gates")

    def test_bash_de_revisor(self):
        for command in ("echo x > app.ts", "sed -i s/a/b/ app.ts", "rm app.ts", "git reset --hard", "git checkout -- .",
                        "git -C /r clean -fd", "git commit -m x", "git pull", "git stash"):
            with self.subTest(command=command):
                self.assertBlocked(self.bash_as("nexus-adversary", command))

    def test_bash_permitido_a_revisor(self):
        for command in ("npm test 2>&1 | head", "git diff main...HEAD", "git -C /r log -5", "grep -r x . > /dev/null",
                        "git status --short"):
            with self.subTest(command=command):
                self.assertAllowed(self.bash_as("nexus-adversary", command))

    def test_bash_a_copia_desechable(self):
        result = self.run_hook("gate", agent_type="nexus-qa", tool_name="Bash", cwd="/home/x/repo", tool_input={"command": "npm test > /tmp/salida.txt"})
        self.assertAllowed(result)

    def test_cd_a_tmp_y_ruta_relativa(self):
        # Falso bloqueo real: el AR de la primera HU real escribia en su scratchpad con cd y ruta relativa.
        for command in ("cd /tmp/claude-1/scratch && cat > vitest.ar.config.ts <<'EOF'\nx\nEOF",
                        "cd '/tmp/s' ; npx vitest run > salida.txt"):
            with self.subTest(command=command):
                self.assertAllowed(self.run_hook("gate", agent_type="nexus-adversary", tool_name="Bash", cwd="/home/x/repo", tool_input={"command": command}))

    def test_cd_que_no_vuelve_desechable(self):
        for command in ("cd /tmp/s && echo x > ../../home/x/repo/app.ts", "cd /tmp/s && cd /home/x/repo && echo x > app.ts",
                        "cd /home/x/repo && echo x > app.ts", "cd /tmp/s && rm -rf /home/x/repo/src", "echo x > app.ts"):
            with self.subTest(command=command):
                self.assertBlocked(self.run_hook("gate", agent_type="nexus-adversary", tool_name="Bash", cwd="/home/x/repo", tool_input={"command": command}))

    def test_variable_asignada_en_el_mismo_comando(self):
        # Falso bloqueo real: el QA de la primera HU real escribia en $S/start con S apuntando a su scratchpad.
        qa = lambda c: self.run_hook("gate", agent_type="nexus-qa", tool_name="Bash", cwd="/home/x/repo", tool_input={"command": c})
        for command in ("S=/tmp/claude-1/s/qa545; mkdir -p $S && date > $S/start", "export S=\"/tmp/s\" && npm test > ${S}/log.txt 2>&1"):
            with self.subTest(command=command):
                self.assertAllowed(qa(command))
        for command in ("S=/tmp/../home/x/repo; echo x > $S/a.ts", "S=/tmp/s; S=/home/x/repo; echo x > $S/a.ts",
                        "S=/tmp/s; S=$(pwd); echo x > $S/a.ts", "echo x > $S/a.ts"):
            with self.subTest(command=command):
                self.assertBlocked(qa(command))

    def test_mayor_que_entre_comillas_no_es_redireccion(self):
        # Falso bloqueo real: un grep de solo lectura con '>' dentro del patron.
        for command in ("grep -n '<nav aria-label=\"Páginas\">' src/a.tsx", "grep -E \"=> |->\" src/a.ts | head",
                        "cat > /tmp/s/a.ts <<'EOF'\nconst f = () => 1 > 0\nEOF"):
            with self.subTest(command=command):
                self.assertAllowed(self.bash_as("nexus-adversary", command))
        for command in ("echo x >\"/home/x/repo/a.ts\"", "grep x a > 'src/salida.txt'", "cat > src/a.ts <<'EOF'\nx\nEOF"):
            with self.subTest(command=command):
                self.assertBlocked(self.bash_as("nexus-adversary", command))

    def test_nombrar_gates_en_una_nota_no_bloquea(self):
        # Segunda HU real: una entrada de bitacora con un heredoc que mencionaba .gates.jsonl.
        for command in ("cat >> doc/sdd/prueba.md <<'EOF'\nel hook escribio .gates.jsonl\nEOF", "echo 'ver .gates.jsonl' >> notas.md",
                        "cat doc/sdd/001/.gates.jsonl", "grep VIOLATION doc/sdd/001/.gates.jsonl | wc -l"):
            with self.subTest(command=command):
                self.assertAllowed(self.bash_as("", command))
        for command in ("echo x >> doc/sdd/001/.gates.jsonl", "sed -i 's/a/b/' doc/sdd/001/.gates.jsonl", "rm doc/sdd/001/.gates.jsonl",
                        "python3 -c \"open('.gates.jsonl','a').write('x')\"", "tee -a .gates.jsonl < x"):
            with self.subTest(command=command):
                self.assertBlocked(self.bash_as("", command), "gates")

    def test_lecturas_reales_de_la_segunda_hu(self):
        # Comandos de solo lectura que el hook bloqueo en la segunda HU real (rutas genericas).
        lecturas = (
            ("nexus-adversary", "cd /home/x/repo; git -C /home/x/repo log --oneline -5; git -C /home/x/repo branch -a --contains abc | head; "
                                "git -C /home/x/repo merge-base --is-ancestor abc origin/main && echo IN || echo OUT"),
            ("nexus-adversary", "cd /tmp/s/copia/apps/web && cp components/a.tsx /tmp/s/a.orig && "
                                "sed -i '3a import { x } from \"../../lib/dato\";' components/a.tsx && head -8 components/a.tsx"),
            ("nexus-adversary", "S=/tmp/s; W=$S/copia/apps/web; cp $S/f.orig $W/components/f.tsx && mkdir -p \"$W/app/zz\" && "
                                "printf 'x' > \"$W/app/zz/error.tsx\" && cat \"$W/app/zz/error.tsx\""),
            ("nexus-supervisor", "cd /tmp; T=/home/x/.claude/projects/p/s/subagents/agent-a.jsonl; wc -l $T; "
                                 "jq -r '.input.command' $T | grep -n -E 'mv |cp |rm |>>|> [^&]|tee |sed -i|python|node -e|perl|git (commit|add)' | cut -c1-300"),
            ("nexus-supervisor", "T=/home/x/.claude/projects/p/s/subagents/agent-a.jsonl; grep -c \"NEXUS GATE\" $T; "
                                 "grep -o '\"command\":\"[^\"]\\{0,200\\}' $T | grep -E \">|tee|sed -i|cp |mv |git (commit|checkout)\" | head"),
            ("nexus-supervisor", "cd /home/x/.claude/projects/p/s/subagents && for f in a.jsonl b.jsonl; do jq -r '.x' $f | "
                                 "grep -n -i \"python\\|node -e\\|tee \\|> *[/$a-zA-Z]\\|cat <<\\|sed -i\\|cp \\|git \" | head -40; done"),
            ("nexus-adversary", "W=/tmp/s/cr/repo/apps/web; F=$W/components/v.tsx; cp $F.orig $F"),
        )
        for agent, command in lecturas:
            with self.subTest(command=command[:60]):
                self.assertAllowed(self.bash_as(agent, command))
        escrituras = (
            ("nexus-adversary", "git -C /home/x/repo merge feat/x"),
            ("nexus-adversary", "cd /tmp/s && cp a.tsx /home/x/repo/src/a.tsx"),
            ("nexus-adversary", "cd /tmp/s && sed -i 's/a/b/' ../../home/x/repo/a.ts"),
            ("nexus-adversary", "S=/tmp/s; W=$S/../../home/x/repo; printf 'x' > \"$W/a.ts\""),
            ("nexus-supervisor", "T=/home/x/repo/a.ts; sed -i 's/a/b/' $T"),
            ("nexus-supervisor", "python3 -c \"open('/home/x/repo/a.ts','w').write('x')\""),
        )
        for agent, command in escrituras:
            with self.subTest(command=command[:60]):
                self.assertBlocked(self.bash_as(agent, command))

    def test_repo_bajo_tmp_no_es_desechable(self):
        self.assertTrue(str(self.repo).startswith(("/tmp", tempfile.gettempdir())))
        self.assertBlocked(self.bash_as("nexus-adversary", f"echo x > {self.repo}/app.ts"))

    def test_no_verify_para_todos(self):
        self.assertBlocked(self.bash_as("nexus-dev", "git commit --no-verify -m x"), "no-verify")
        self.assertBlocked(self.bash_as("", "git push --no-verify"), "no-verify")

    def test_dev_puede_commitear(self):
        self.assertAllowed(self.bash_as("nexus-dev", "git add -A && git commit -m x"))

    def test_interprete_en_linea_que_escribe(self):
        for command in ("python3 -c \"open('sdd.md','w').write('x')\"", "node -e \"require('fs').writeFileSync('a','b')\"",
                        "perl -pi -e 's/a/b/' app.ts"):
            with self.subTest(command=command):
                self.assertBlocked(self.bash_as("nexus-architect", command), "")

    def test_interprete_que_solo_lee(self):
        self.assertAllowed(self.bash_as("nexus-adversary", "node -e \"console.log(require('./app'))\""))

    def test_agujero_conocido_sigue_documentado(self):
        # Si un dia se cierra, este test avisa que hay que corregir enforcement.md.
        self.assertAllowed(self.bash_as("nexus-adversary", "python3 scripts/escribe.py"))

    def _context(self, text):
        (self.repo / "project-context.md").write_text(text)

    def test_comando_prohibido_por_el_proyecto(self):
        self._context("| **forbidden_commands** | `supabase db push|vercel .*--prod` |\n")
        for agent in ("nexus-dev", "", "nexus-qa"):
            with self.subTest(agent=agent):
                self.assertBlocked(self.bash_as(agent, "supabase db push"), "prohibe")
        self.assertAllowed(self.bash_as("nexus-dev", "supabase status"))

    def test_barra_escapada_de_la_tabla_es_alternativa(self):
        # Como en la plantilla: dentro de una tabla Markdown la barra va escapada.
        self._context("| **forbidden_commands** | `supabase db push\\|gh pr merge` |\n")
        self.assertBlocked(self.bash_as("", "gh pr merge 3 --merge"), "prohibe")
        self.assertBlocked(self.bash_as("nexus-dev", "supabase db push"), "prohibe")
        self.assertAllowed(self.bash_as("", "gh pr create --draft"))

    def test_sin_lista_no_se_prohibe(self):
        self._context("| **gate_command** | `x` |\n")
        self.assertAllowed(self.bash_as("nexus-dev", "supabase db push"))

    def test_expresion_invalida_bloquea(self):
        self._context("forbidden_commands: `(`\n")
        self.assertBlocked(self.bash_as("nexus-dev", "ls"), "no es una expresion")

    def test_contexto_en_nexus_root(self):
        other = self.tmp / "nexus"
        other.mkdir()
        (other / "project-context.md").write_text("forbidden_commands: `db push`\n")
        self.write("work-item.md", "- Pipeline: FAST\n")
        prompt = f"RUTAS: NEXUS_ROOT={other} · CODE_ROOT={self.repo}\nFASE: F1\nHU_DIR: {self.hu}\nhaz"
        self.assertAllowed(self.run_hook("gate", tool_name="Agent", tool_input={"subagent_type": "nexus-analyst", "prompt": prompt}))
        self.assertBlocked(self.run_hook("gate", agent_type="nexus-dev", tool_name="Bash", cwd=str(self.tmp), tool_input={"command": "supabase db push"}), "prohibe")


class AlTerminar(HookCase):
    def stop(self, agent):
        return self.run_hook("stop", agent_type=agent)

    def test_revisor_cambio_el_arbol(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        (self.repo / "app.ts").write_text("cambiado\n")
        self.write("ar-report.md", "STATUS: APROBADO open_blq=0\n")
        self.assertIn("arbol de git cambio", self.stop("nexus-adversary").stdout)

    def test_arquitecto_cambio_el_arbol(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.spawn("F2")
        (self.repo / "app.ts").write_text("cambiado\n")
        self.write("sdd.md")
        self.assertIn("arbol de git cambio", self.stop("nexus-architect").stdout)

    def test_artefactos_no_cuentan_como_cambio(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        self.write("ar-report.md", "STATUS: APROBADO open_blq=0\n")
        self.assertEqual(self.stop("nexus-adversary").stdout, "")

    def test_analista_sin_seccion_de_preguntas(self):
        self.spawn("F1", "nexus-analyst")
        self.write("work-item.md", "# WI\n")
        self.assertIn("PREGUNTAS PARA EL HUMANO", self.stop("nexus-analyst").stdout)

    def test_analista_con_seccion(self):
        self.spawn("F1", "nexus-analyst")
        self.write("work-item.md", "# WI\n## PREGUNTAS PARA EL HUMANO\nNinguna\n## MEMORIA CONSULTADA\nNinguna: sin Engram\n")
        self.assertEqual(self.stop("nexus-analyst").stdout, "")

    def test_analista_sin_memoria_consultada(self):
        self.spawn("F1", "nexus-analyst")
        self.write("work-item.md", "# WI\n## PREGUNTAS PARA EL HUMANO\nNinguna\n")
        self.assertIn("MEMORIA CONSULTADA", self.stop("nexus-analyst").stdout)

    def test_falta_reporte(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        self.assertIn("ar-report.md", self.stop("nexus-adversary").stdout)

    def test_falta_status(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        self.write("ar-report.md", "sin linea\n")
        self.assertIn("STATUS", self.stop("nexus-adversary").stdout)

    def test_no_insiste_dos_veces(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        self.assertEqual(self.run_hook("stop", agent_type="nexus-adversary", stop_hook_active=True).stdout, "")

    def test_ar_y_cr_paralelos_por_transcript(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        self.spawn("CR", "nexus-adversary")
        transcript = self.tmp / "cr.jsonl"
        transcript.write_text(json.dumps({"message": "FASE: CR\nHU_DIR: x"}) + "\n")
        self.write("cr-report.md", "STATUS: APROBADO open_blq=0\n")
        result = self.run_hook("stop", agent_type="nexus-adversary", agent_transcript_path=str(transcript))
        self.assertEqual(result.stdout, "")

    def test_qa_sin_comandos(self):
        self.write("work-item.md", "pipeline: FAST\n")
        self.spawn("F4", "nexus-qa")
        self.write("validation.md", "STATUS: APROBADO PARA DONE\n")
        transcript = self.tmp / "qa.jsonl"
        transcript.write_text(json.dumps({"message": "FASE: F4"}) + "\n")
        result = self.run_hook("stop", agent_type="nexus-qa", agent_transcript_path=str(transcript))
        self.assertIn("no ejecuto", result.stdout)

    def test_session_recuerda_la_hu(self):
        self.write("work-item.md")
        self.spawn("F1", "nexus-analyst")
        self.assertIn("001-demo", self.run_hook("session").stdout)


class PorDestino(HookCase):
    """Rodeo real de la prueba: el arquitecto escribio sdd.md con un script de Python lanzado por Bash."""

    def bash(self, agent, phase, command, tool_use_id="t1"):
        self.assertAllowed(self.spawn(phase, agent))
        data = dict(agent_type=f"nexus-agile:{agent}", tool_name="Bash", tool_use_id=tool_use_id, tool_input={"command": command})
        before = self.run_hook("gate", **data)
        return before, data

    def test_script_que_cambia_un_artefacto(self):
        self.write("work-item.md", "v1\n")
        before, data = self.bash("nexus-analyst", "F1", "python3 /tmp/s/ajustar.py")
        self.assertAllowed(before)
        self.write("work-item.md", "v2\n")  # lo que hizo el script
        self.assertBlocked(self.run_hook("after-bash", **data), "work-item.md")
        gates = [json.loads(l) for l in (self.hu / ".gates.jsonl").read_text().splitlines()]
        self.assertEqual(gates[-1]["gate"], "VIOLATION")
        self.assertEqual((self.hu / "work-item.md").read_text(), "v1\n")  # restaurado
        self.assertEqual([p.read_text() for p in (self.hu / ".violations").iterdir()], ["v2\n"])  # lo modificado, para la persona
        stop = self.run_hook("stop", agent_type="nexus-agile:nexus-analyst")
        self.assertIn("con Bash", stop.stdout)

    def test_archivo_creado_por_bash_se_retira(self):
        _, data = self.bash("nexus-analyst", "F1", "python3 /tmp/s/x.py")
        self.write("sdd.md", "inventado\n")
        self.assertBlocked(self.run_hook("after-bash", **data), "sdd.md")
        self.assertFalse((self.hu / "sdd.md").exists())
        self.assertTrue(any((self.hu / ".violations").glob("sdd.md.*")))

    def test_bash_que_no_cambia_nada(self):
        self.write("sdd.md", "v1\n")
        _, data = self.bash("nexus-analyst", "F1", "grep -n x sdd.md")
        self.assertAllowed(self.run_hook("after-bash", **data))
        self.assertFalse((self.hu / ".gates.jsonl").exists() and "VIOLATION" in (self.hu / ".gates.jsonl").read_text())

    def test_write_concurrente_no_es_violacion(self):
        # AR y CR en paralelo: el AR escribe su reporte con Write mientras el CR corre un Bash.
        _, data = self.bash("nexus-analyst", "F1", "npx vitest run", tool_use_id="cr1")
        self.assertTrue(any(self.tmp.glob("data/bash-*.json")))
        report = self.hu / "ar-report.md"
        self.assertAllowed(self.run_hook("gate", agent_type="nexus-agile:nexus-adversary", tool_name="Write", tool_input={"file_path": str(report)}))
        report.write_text("STATUS: APROBADO open_blq=0\n")
        self.assertAllowed(self.run_hook("after-bash", **data))

    def test_sed_sobre_un_artefacto_se_frena_antes(self):
        # HU-4 de Nexus Control: el dev corrio sed -i sobre auto-blindaje.md y el git commit del mismo comando lo guardo.
        self.write("work-item.md", "- Pipeline: FAST\n## PREGUNTAS PARA EL HUMANO\nNinguna\n")
        self.type_gate("HU_APPROVED")
        self.write("auto-blindaje.md", "v1\n")
        rel = self.hu.relative_to(self.repo)
        cmd = (f"cd {self.repo}; S=/tmp/sp/F3-011-fp1; /usr/bin/sed -i '35s/aserción/asercion/' {rel}/auto-blindaje.md; "
               f"/usr/bin/grep -cP '[^\\x00-\\x7F]' {rel}/auto-blindaje.md\ngit add {rel}/auto-blindaje.md && git commit -q -m x")
        before, _ = self.bash("nexus-dev", "F3", cmd)
        self.assertBlocked(before, "auto-blindaje.md")
        dev = dict(agent_type="nexus-agile:nexus-dev", tool_name="Bash")
        for other in (f"tee {self.hu}/sdd.md < /tmp/x", f"cd {self.hu} && cp /tmp/x sdd.md", f"rm {self.hu}/sdd.md",
                      f"cd {self.hu}; sed -i 's/a b/c/' sdd.md"):
            self.assertBlocked(self.run_hook("gate", tool_input={"command": other}, **dev))
        # Leer un artefacto, copiarlo afuera o editar codigo sigue permitido; un script de sed con espacios no es un archivo
        for fine in (f"cp {self.hu}/sdd.md /tmp/sp/sdd.md", f"sed -n 1,5p {self.hu}/sdd.md",
                     f"cd {self.hu}; sed -i 's/a b/c/' /tmp/sp/x.md", f"cd {self.repo} && sed -i 's/a/b/' src/a.py && git add src/a.py"):
            self.assertAllowed(self.run_hook("gate", tool_input={"command": fine}, **dev))

    def test_sesion_principal_no_se_vigila(self):
        self.write("sdd.md", "v1\n")
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))
        data = dict(tool_name="Bash", tool_use_id="m1", tool_input={"command": "cp /tmp/x sdd.md"})
        self.assertAllowed(self.run_hook("gate", **data))
        self.write("sdd.md", "v2\n")
        self.assertAllowed(self.run_hook("after-bash", **data))


class Versiones(HookCase):
    def test_cada_entrega_queda_en_versions(self):
        # Segunda HU real: la v1 del work-item se perdio porque .versions/ solo se llenaba al aprobar.
        for text in ("v1\n## PREGUNTAS PARA EL HUMANO\n- [ ] x\n", "v2\n## PREGUNTAS PARA EL HUMANO\nNinguna\n"):
            self.assertAllowed(self.spawn("F1", "nexus-analyst"))
            self.write("work-item.md", text)
            self.run_hook("stop", agent_type="nexus-agile:nexus-analyst")
        self.assertEqual(len(list((self.hu / ".versions").glob("work-item-*.md"))), 2)


    def test_agente_retomado_tambien_deja_version(self):
        # HU-3 de Nexus Control: el arquitecto corrigio el SDD dos veces retomado con SendMessage, y esas versiones no quedaron.
        transcript = self.tmp / "agent-arq.jsonl"
        transcript.write_text(json.dumps({"message": {"role": "user", "content": "FASE: F2\nhaz"}}) + "\n")
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))
        for n in (1, 2, 3):
            self.write("work-item.md", f"v{n}\n## PREGUNTAS PARA EL HUMANO\nNinguna\n## MEMORIA CONSULTADA\nNinguna\n")
            self.run_hook("stop", agent_type="nexus-agile:nexus-analyst", agent_transcript_path=str(transcript))
        self.assertEqual(len(list((self.hu / ".versions").glob("work-item-*.md"))), 3)
        # Otro agente que nunca se lanzo no hereda nada
        self.write("work-item.md", "v4\n")
        self.run_hook("stop", agent_type="nexus-agile:nexus-dev")
        self.assertEqual(len(list((self.hu / ".versions").glob("work-item-*.md"))), 3)


class Supervision(HookCase):
    def consult(self, answer, name="sup.jsonl"):
        transcript = self.tmp / name
        prompt = f"FASE: SUPERVISION\nHU_DIR: {self.hu}\nPunto de parada: fin de F0+F1 de GH-11, en AUTO\nRevisa."
        lines = [{"message": {"role": "user", "content": prompt}},
                 {"message": {"role": "assistant", "content": [{"type": "tool_use", "name": "SubagentHandback", "input": {"message": answer}}]}}]
        transcript.write_text("".join(json.dumps(l) + "\n" for l in lines))
        self.assertAllowed(self.spawn("SUPERVISION", "nexus-supervisor"))
        return self.run_hook("stop", agent_type="nexus-agile:nexus-supervisor", agent_transcript_path=str(transcript))

    def test_el_veredicto_queda_en_gates(self):
        # HU-4 de Nexus Control: para contar los veredictos hubo que leerlos de los transcripts.
        self.consult("VEREDICTO: ESCALAR\n\n**Qué comprobé**\n- todo")
        entry = [json.loads(l) for l in (self.hu / ".gates.jsonl").read_text().splitlines()][-1]
        self.assertEqual((entry["gate"], entry["verdict"], entry["by"]), ("SUPERVISION", "ESCALAR", "nexus-supervisor"))
        self.assertEqual(entry["point"], "fin de F0+F1 de GH-11, en AUTO")

    def test_sin_veredicto_se_le_pide_el_formato(self):
        stop = self.consult("Revise todo y esta bien.", name="sup2.jsonl")
        self.assertIn("VEREDICTO", stop.stdout + stop.stderr)
        entry = [json.loads(l) for l in (self.hu / ".gates.jsonl").read_text().splitlines()][-1]
        self.assertIsNone(entry["verdict"])


class GateDelegadoRevisado(HookCase):
    """El hook registraba el gate delegado sin mirar si hubo revision. Con --supervisor, ahora la exige."""

    def setUp(self):
        super().setUp()
        self.write("work-item.md")
        self.run_hook("prompt", prompt="/nexus-agile:nexus-auto X-1 --supervisor")
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))  # deja la HU en la sesion

    def review(self, verdict, ago=0):
        with (self.hu / ".gates.jsonl").open("a") as handle:
            handle.write(json.dumps({"gate": "SUPERVISION", "by": "nexus-supervisor", "verdict": verdict, "ts": int(time.time()) - ago}) + "\n")

    def test_sin_revision_no_pasa(self):
        self.assertBlocked(self.spawn("F2"), "veredicto del supervisor")

    def test_continuar_registra_el_gate(self):
        self.review("CONTINUAR")
        self.assertAllowed(self.spawn("F2"))
        self.assertIn("claude-delegated", (self.hu / ".gates.jsonl").read_text())

    def test_escalar_espera_a_la_persona(self):
        self.review("ESCALAR")
        self.assertBlocked(self.spawn("F2"), "respuesta de la persona")
        self.run_hook("prompt", prompt="Si, sigue con la opcion A")
        decision = [json.loads(l) for l in (self.hu / ".gates.jsonl").read_text().splitlines()][-1]
        self.assertEqual((decision["gate"], decision["via"]), ("DECISION", "texto"))
        self.assertAllowed(self.spawn("F2"))

    def test_respuesta_en_la_ventana_cuenta(self):
        self.review("ESCALAR")
        self.run_hook("answer", tool_name="AskUserQuestion", tool_response={"answers": {"Sigo?": "Si"}})
        self.assertAllowed(self.spawn("F2"))

    def test_revision_de_una_version_anterior_no_cuenta(self):
        self.review("CONTINUAR", ago=100)
        self.write("work-item.md", "cambiado\n")
        self.assertBlocked(self.spawn("F2"), "version actual")

    def test_pedir_evidencia_no_pasa(self):
        self.review("PEDIR_EVIDENCIA")
        self.assertBlocked(self.spawn("F2"), "PEDIR_EVIDENCIA")

    def test_sin_escalado_pendiente_un_mensaje_no_es_decision(self):
        self.review("CONTINUAR")
        self.run_hook("prompt", prompt="como va?")
        self.assertNotIn("DECISION", (self.hu / ".gates.jsonl").read_text())


class Concurrencia(HookCase):
    def test_hooks_en_paralelo_no_corrompen_el_estado(self):
        # HU-2 de Nexus Control: con AR y CR en paralelo, el hook leyo el estado vacio y freno un mensaje.
        import concurrent.futures
        self.write("work-item.md")
        self.run_hook("prompt", prompt="/nexus-agile:nexus-auto X-1")
        def golpe(i):
            if i % 2:
                return self.run_hook("prompt", prompt=f"como va {i}")
            return self.run_hook("gate", agent_type="nexus-agile:nexus-adversary", tool_name="Bash", tool_use_id=f"t{i}",
                                 tool_input={"command": "git -C /x log --oneline -1"})
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            results = list(pool.map(golpe, range(40)))
        self.assertEqual([r.returncode for r in results if r.returncode not in (0,)], [])
        state = json.loads(next((self.tmp / "data").glob("s1.json")).read_text())
        self.assertTrue(state["delegated"])

    def test_fotos_viejas_se_borran(self):
        data = self.tmp / "data"
        data.mkdir(exist_ok=True)
        old = data / "bash-viejo.json"
        old.write_text("{}")
        os.utime(old, (1, 1))
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))
        self.run_hook("gate", agent_type="nexus-agile:nexus-analyst", tool_name="Bash", tool_use_id="n1", tool_input={"command": "ls"})
        self.assertFalse(old.exists())


class TerceraHU(HookCase):
    """Comandos literales (rutas genericas) que el hook bloqueo por error en la HU-2 de Nexus Control."""

    def bash_as(self, agent, command):
        return self.run_hook("gate", agent_type=agent, tool_name="Bash", cwd="/home/x/repo", tool_input={"command": command})

    def test_cd_despues_de_asignar_variables(self):
        cmd = ("S=/tmp/sp; rm -rf $S/p; P=$S/p; mkdir -p $P/doc/sdd/005-hu $P/doc/sdd/007-otra; D=$P/doc/sdd/005-hu\n"
               "cd $D; printf 'x' > work-item.md; printf 'x' > sdd.md\nprintf 'STATUS: APROBADO\\n' > cr-report.md")
        self.assertAllowed(self.bash_as("nexus-qa", cmd))
        self.assertBlocked(self.bash_as("nexus-qa", "S=/home/x/repo; cd $S; printf 'x' > work-item.md"))
        # Un cd en un subshell no cuenta para el resto del comando
        self.assertAllowed(self.bash_as("nexus-qa", "D=/tmp/sp/hu; cd $D; printf x > .gates.jsonl; (cd /tmp/sp && find . -type f | sort) > /tmp/sp/after.txt"))
        self.assertBlocked(self.bash_as("nexus-qa", "(cd /tmp/sp && ls); printf x > .gates.jsonl"), "gates")
        # Varios cd seguidos: vale el ultimo antes de cada ruta
        self.assertAllowed(self.bash_as("nexus-qa", "cd /tmp/sp/hu; printf x > .gates.jsonl; cd /; find /tmp/sp -type f"))
        self.assertBlocked(self.bash_as("nexus-qa", "cd /tmp/sp; cd /home/x/repo/doc/sdd/005; printf x > .gates.jsonl"), "gates")
        self.assertBlocked(self.bash_as("nexus-qa", "cd /tmp/sp; cd ..; printf x > .gates.jsonl"), "gates")

    def test_gates_de_prueba_con_rm_o_sed_en_tmp(self):
        cmd = ("S=/tmp/sp; rm -rf $S/p; P=$S/p; D=$P/doc/sdd/005-hu; mkdir -p $D $D/.violations\n"
               "python3 - $D/.gates.jsonl <<'EOF'\nimport json,sys\nopen(sys.argv[1],'w').write('{}')\nEOF")
        self.assertAllowed(self.bash_as("nexus-qa", cmd))
        cmd2 = ("S=/tmp/sp/re-ar; /usr/bin/sed -i 's/a/b/' $S/src/reader.py\nP=$S/proj; mkdir -p $P/doc/sdd/005-x\n"
                "printf '%s\\n' '{}' > $P/doc/sdd/005-x/.gates.jsonl")
        self.assertAllowed(self.bash_as("nexus-adversary", cmd2))
        self.assertBlocked(self.bash_as("nexus-qa", "S=/home/x/repo; rm -f x; printf '{}' > $S/doc/sdd/005/.gates.jsonl"), "gates")
        self.assertBlocked(self.bash_as("nexus-qa", "cp /tmp/a /home/x/repo/doc/sdd/005/.gates.jsonl"), "gates")

    def test_asignacion_dentro_de_un_heredoc_no_cuenta(self):
        # HU-3 de Nexus Control: S="$S/..." en el cuerpo del script de QA anulaba el S del comando.
        cmd = ("cd /home/x/repo; S=/tmp/sp/qa; rm -rf $S; mkdir -p $S/p/sess1/subagents\n"
               "H=/home/x/repo/doc/sdd/007-costo\ncat > $S/mk.py <<EOF\nimport json,sys\nS=\"$S/p/sess1/subagents/\"\nH=\"$H\"\nEOF\n"
               "python3 $S/mk.py")
        self.assertAllowed(self.bash_as("nexus-qa", cmd))
        # Reasignar en el shell, fuera del heredoc, sigue sin resolverse
        self.assertBlocked(self.bash_as("nexus-qa", "S=/tmp/sp; S=/home/x/repo; printf x > $S/mk.py"))
        # Con un cd al repo, lo que se borra o copia en /tmp sigue siendo desechable; en el repo, no
        self.assertAllowed(self.bash_as("nexus-qa", "cd /home/x/repo; S=/tmp/sp/qa; rm -rf $S; cp src/a.py $S/a.py"))
        self.assertBlocked(self.bash_as("nexus-qa", "cd /home/x/repo; rm -f src/a.py"))
        self.assertBlocked(self.bash_as("nexus-qa", "cd /home/x/repo; cp /tmp/a src/a.py"))
        self.assertBlocked(self.bash_as("nexus-qa", "cd /home/x/repo; sed -i 's/a/b/' src/a.py /tmp/b"))
        self.assertBlocked(self.bash_as("nexus-qa", "cd /home/x/repo; mv src/a.py /tmp/sp/a.py"))
        # Una copia de respaldo a /tmp no habilita un script en linea que escribe en el repo
        self.assertBlocked(self.bash_as("nexus-adversary", "cd /home/x/repo && cp src/a.py /tmp/sp/a.bak && python3 - <<'PY'\np='/home/x/repo/src/a.py'\nopen(p,'w').write('x')\nPY"))

    def test_sin_cd_cada_archivo_se_juzga_por_su_ruta(self):
        # Antes alcanzaba con una palabra en /tmp: `rm src/a.py /tmp/x` pasaba.
        self.assertBlocked(self.bash_as("nexus-qa", "rm src/a.py /tmp/sp/x"))
        self.assertBlocked(self.bash_as("nexus-adversary", "cp /tmp/sp/orig.ts /home/x/repo/src/a.ts"))
        self.assertAllowed(self.bash_as("nexus-qa", "rm -rf /tmp/sp/x && mkdir -p /tmp/sp/x && cp /home/x/repo/src/a.py /tmp/sp/x/"))
        # Subcomandos de otra herramienta no son mutaciones de archivos locales
        self.assertAllowed(self.bash_as("nexus-adversary", "docker cp /tmp/sp/supabase pg:/rama && docker rm -f pg"))
        # Una carpeta de mktemp en /tmp es desechable; una plantilla relativa cae en el directorio actual
        self.assertAllowed(self.bash_as("nexus-adversary", "D=$(mktemp -d /tmp/cr001mut.XXXX); cp /home/x/repo/tests/a.py $D/; sed -i 's/a/b/' $D/a.py"))
        self.assertAllowed(self.bash_as("nexus-adversary", "T=$(mktemp -d); cp /home/x/repo/a.py $T/a.py"))
        self.assertBlocked(self.bash_as("nexus-adversary", "D=$(mktemp -d copia.XXXX); cp /tmp/a $D/a.py"))

    def test_falsos_positivos_del_parser_en_corridas_reales(self):
        # Rejugando los comandos reales: --rm de docker run, 2>/dev/null, la barra de continuacion y un cd relativo.
        self.assertAllowed(self.bash_as("nexus-qa", "docker run --rm -v /tmp/sp/supabase:/work -w /work postgres psql -f x.sql"))
        self.assertAllowed(self.bash_as("nexus-qa", "cp /home/x/repo/a.md /tmp/sp/a.md 2>/dev/null; rm -f /tmp/sp/b 2>&1"))
        self.assertAllowed(self.bash_as("nexus-qa", "cp /home/x/repo/a.md \\\n  /tmp/sp/a.md"))
        self.assertAllowed(self.bash_as("nexus-adversary", "cd /tmp/sp/wt || exit 1\ncd apps/web && rm -rf .next"))
        self.assertBlocked(self.bash_as("nexus-adversary", "cd /tmp/sp/wt; cd ..; cd x && rm -rf y"))
        # La variable de un for cuenta como /tmp solo si el comando nombra /tmp
        self.assertAllowed(self.bash_as("nexus-adversary", "cd /tmp/sp/wt; for f in a.ts b.ts; do cp /tmp/sp/orig/$f $f; done"))
        self.assertBlocked(self.bash_as("nexus-adversary", "for f in a.ts b.ts; do rm $f; done"))
        # tee dentro de una ruta no es tee; cd con redireccion antes del ||; variables de una funcion
        self.assertAllowed(self.bash_as("nexus-qa", "L=$(ls -t ~/.local/share/rtk/tee/*vitest_run.log | head -1); head -1 \"$L\" > /tmp/sp/v.txt"))
        self.assertAllowed(self.bash_as("nexus-adversary", "cd /tmp/sp/lab 2>/dev/null || exit 1\ncp src/a.ts /tmp/sp/a.bak"))
        self.assertAllowed(self.bash_as("nexus-adversary", "S=/tmp/sp/ar; x() { M=$1; D=$S/$M; mkdir -p $D; cp /home/x/repo/a.py $D/; }; x m1"))
        self.assertAllowed(self.bash_as("nexus-qa", "npx vitest run 2>&1 | /usr/bin/tee /tmp/sp/v.log"))
        self.assertBlocked(self.bash_as("nexus-qa", "npx vitest run 2>&1 | tee /home/x/repo/v.log"))
        # Corrida real: python3 -I -c que muta un archivo del repo, con la ruta en una variable relativa y un cp que lo restaura
        self.assertBlocked(self.bash_as("nexus-adversary", "cd /home/x/repo/apps/web && f=lib/a.ts; python3 -I -c 'import sys;f=sys.argv[1];open(f,\"w\").write(\"x\")' $f; npx vitest run > /tmp/sp/mf.txt 2>&1; cp /tmp/sp/bk2 $f"))
        # Un script en linea despues de un cd a /tmp, con copias desde el repo: el script escribe en la copia
        self.assertAllowed(self.bash_as("nexus-adversary", "SP=/tmp/sp; R=/home/x/repo; cp $R/src/a.ts $SP/repo/src/a.ts; python3 - <<'EOF'\np='/tmp/sp/repo/src/a.ts'\nopen(p,'w').write('x')\nEOF\ncd $SP/repo && npx tsc --noEmit"))

    def test_carpeta_de_evidencia_declarada(self):
        # En un proyecto real, los revisores dejaban evidencia en una carpeta de auditoria fuera del repo.
        (self.repo / "project-context.md").write_text("| **evidence_dir** | `/home/x/auditoria` |\n")
        repo = dict(agent_type="nexus-agile:nexus-qa", tool_name="Bash", cwd=str(self.repo))
        self.assertAllowed(self.run_hook("gate", tool_input={"command": "cp /tmp/sp/qa.md /home/x/auditoria/s1/qa.md"}, **repo))
        self.assertAllowed(self.run_hook("gate", tool_input={"command": "npx vitest run 2>&1 | tee /home/x/auditoria/s1/tests.txt"}, **repo))
        self.assertBlocked(self.run_hook("gate", tool_input={"command": "cp /tmp/sp/qa.md /home/x/otra/qa.md"}, **repo))
        # Una carpeta de evidencia que contiene el repo no cuenta
        (self.repo / "project-context.md").write_text(f"| **evidence_dir** | `{self.repo.parent}` |\n")
        self.assertBlocked(self.run_hook("gate", tool_input={"command": f"cp /tmp/a {self.repo}/src/a.py"}, **repo))

    def test_git_stash_list_es_lectura(self):
        self.assertAllowed(self.bash_as("nexus-adversary", "cd /home/x/repo && git stash list | head -2; git diff main --stat -- tests"))
        self.assertBlocked(self.bash_as("nexus-adversary", "git -C /home/x/repo stash"), "git")
        self.assertBlocked(self.bash_as("nexus-adversary", "git -C /home/x/repo stash pop"), "git")

    def test_artefacto_por_bash_pide_write(self):
        out = self.bash_as("nexus-qa", "cd /home/x/repo; cat > doc/sdd/005-tablero/validation-2.md <<'EOF'\nSTATUS: APROBADO\nEOF")
        self.assertBlocked(out, "Write o Edit")


class EstadoDeLaHU(HookCase):
    def test_repetir_una_fase_no_reabre_una_hu_cerrada(self):
        # QA corto sobre una HU en DONE: el estado pasaba de DONE a F4.
        self.write("work-item.md")
        self.write("ar-report.md", "STATUS: APROBADO open_blq=0\n")
        self.write("cr-report.md", "STATUS: APROBADO open_blq=0\n")
        (self.hu / ".nexus-state.json").write_text(json.dumps({"phase": "DONE", "status": "done"}))
        self.write("work-item.md", "- Pipeline: FAST\n")
        self.assertAllowed(self.spawn("F4", "nexus-qa"))
        state = json.loads((self.hu / ".nexus-state.json").read_text())
        self.assertEqual((state["phase"], state["status"]), ("DONE", "done"))
        self.assertEqual(state["rerun"]["phase"], "F4")


class ProyectoNuevo(HookCase):
    """Fricciones de la primera HU de un proyecto nuevo."""

    def bash_as(self, agent, command):
        return self.run_hook("gate", agent_type=agent, tool_name="Bash", cwd="/home/x/repo", tool_input={"command": command})

    def test_sonda_de_python_de_solo_lectura(self):
        for agent in ("nexus-architect", "nexus-security", "nexus-adversary"):
            with self.subTest(agent=agent):
                self.assertAllowed(self.bash_as(agent, 'python3 -P -c "import sys; print(sys.path)" >/dev/null 2>&1; echo $?'))
        self.assertBlocked(self.bash_as("nexus-architect", 'python3 -c "open(\'/home/x/repo/a\',\'w\').write(\'x\')"'))

    def test_gates_de_prueba_en_tmp(self):
        self.assertAllowed(self.bash_as("nexus-qa", "printf '{}' > /tmp/fx/doc/sdd/001/.gates.jsonl"))
        # El comando literal que bloqueo la rc.5 en el QA corto: cd a /tmp y ruta relativa, en varias lineas.
        literal = ("cd /tmp/nc-qa2; mkdir -p proj-ac2/doc/sdd/001-alfa proj-ac6/doc/sdd/001-beta\n"
                   "printf '{\"gate\":\"HU_APPROVED\",\"by\":\"ana\"}\\n' > proj-ac2/doc/sdd/001-alfa/.gates.jsonl; echo EXIT=$?")
        self.assertAllowed(self.bash_as("nexus-qa", literal))
        self.assertBlocked(self.bash_as("nexus-qa", "cd /tmp/x; printf '{}' > ../../home/x/repo/doc/sdd/001/.gates.jsonl"), "gates")
        self.assertBlocked(self.bash_as("nexus-qa", "printf '{}' > doc/sdd/001/.gates.jsonl"), "gates")
        self.assertAllowed(self.bash_as("nexus-qa", "cd /tmp/nc-qa2 && cp base.jsonl proj-ac6/doc/sdd/001-beta/.gates.jsonl"))
        self.assertBlocked(self.bash_as("nexus-qa", "cd /tmp/nc-qa2 && cp base.jsonl /home/x/repo/doc/sdd/001/.gates.jsonl"), "gates")
        self.assertAllowed(self.run_hook("gate", agent_type="nexus-agile:nexus-adversary", tool_name="Write",
                                         tool_input={"file_path": "/tmp/fx/doc/sdd/001/.gates.jsonl"}))
        self.assertBlocked(self.run_hook("gate", agent_type="nexus-agile:nexus-adversary", tool_name="Write",
                                         tool_input={"file_path": str(self.hu / ".gates.jsonl")}), "gates")

    def test_dev_no_escribe_artefactos_por_bash_ni_con_commit(self):
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))
        cmd = f"cat > {self.hu}/auto-blindaje.md <<'EOF'\nx\nEOF\ngit add -A && git commit -qm w2"
        self.assertBlocked(self.run_hook("gate", agent_type="nexus-agile:nexus-dev", tool_name="Bash", tool_input={"command": cmd}), "Write o Edit")
        rel = "cd " + str(self.repo) + " && echo x >> doc/sdd/001-demo/auto-blindaje.md"
        self.assertBlocked(self.run_hook("gate", agent_type="nexus-agile:nexus-dev", tool_name="Bash", tool_input={"command": rel}), "Write o Edit")
        self.assertAllowed(self.run_hook("gate", agent_type="nexus-agile:nexus-dev", tool_name="Bash",
                                         tool_input={"command": "npm test > /tmp/s/gate.log 2>&1"}))

    def test_gate_dentro_de_un_mensaje_avisa(self):
        self.write("work-item.md")
        out = self.run_hook("prompt", prompt="agregalo al Scope OUT y HU_APPROVED")
        self.assertIn("NO se registro", out.stdout)
        self.assertFalse((self.hu / ".gates.jsonl").exists())

    def test_caracteres_invisibles_en_artefactos(self):
        self.spawn("F1", "nexus-analyst")
        self.write("work-item.md", "# WI\n## PREGUNTAS PARA EL HUMANO\nNinguna\n## MEMORIA CONSULTADA\nNinguna\nAC-1: el total \u202esin descuento\n")
        out = self.run_hook("stop", agent_type="nexus-agile:nexus-analyst")
        self.assertIn("U+202E", out.stdout)


if __name__ == "__main__":
    unittest.main()
