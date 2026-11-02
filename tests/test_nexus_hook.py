#!/usr/bin/env python3
"""Pruebas de los hooks con entradas como las de Claude Code. Sin modelo y sin red."""
import json
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
        prompt = f"RUTAS: CODE_ROOT={self.repo}\nFASE: {phase}\nHU_DIR: {self.hu}\nhaz"
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

    def test_fase_desconocida(self):
        self.assertBlocked(self.spawn("F9"), "desconocida")

    def test_f1_sin_precondiciones(self):
        self.assertAllowed(self.spawn("F1", "nexus-analyst"))

    def test_f2_sin_artefacto(self):
        self.assertBlocked(self.spawn("F2"), "work-item.md")

    def test_f2_sin_gate(self):
        self.write("work-item.md")
        self.assertBlocked(self.spawn("F2"), "HU_APPROVED")

    def test_f2_con_gate(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.assertAllowed(self.spawn("F2"))

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

    def _hasta_spec(self):
        self.write("work-item.md")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md")
        self.type_gate("SPEC_APPROVED")

    def test_f3_quality_sin_contrato(self):
        self._hasta_spec()
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "story-file.md")

    def test_f3_quality_con_story(self):
        self._hasta_spec()
        self.write("story-file.md")
        self.assertAllowed(self.spawn("F3", "nexus-dev"))

    def test_f3_unified_exige_seccion(self):
        self.write("work-item.md", "contract_mode: unified\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md")
        self.type_gate("SPEC_APPROVED")
        self.assertBlocked(self.spawn("F3", "nexus-dev"), "Contrato")

    def test_f3_unified_con_seccion(self):
        self.write("work-item.md", "contract_mode: unified\n")
        self.type_gate("HU_APPROVED")
        self.write("sdd.md", "## Contrato de implementacion\n")
        self.type_gate("SPEC_APPROVED")
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

    def test_qa_no_escribe_reporte_ajeno(self):
        self.assertBlocked(self.write_as("nexus-qa", self.hu / "ar-report.md"))

    def test_qa_escribe_en_copia_desechable(self):
        self.assertAllowed(self.run_hook("gate", agent_type="nexus-qa", tool_name="Write", cwd="/home/x/repo", tool_input={"file_path": "/tmp/copia/x.ts"}))

    def test_arquitecto_no_toca_codigo(self):
        self.assertBlocked(self.write_as("nexus-architect", self.repo / "app.ts"))

    def test_dev_escribe_codigo(self):
        self.assertAllowed(self.write_as("nexus-dev", self.repo / "app.ts"))

    def test_sesion_principal_no_se_limita(self):
        self.assertAllowed(self.write_as("", self.repo / "app.ts"))

    def test_nadie_escribe_gates(self):
        self.assertBlocked(self.write_as("nexus-dev", self.hu / ".gates.jsonl"), "gates")
        self.assertBlocked(self.bash_as("nexus-dev", f"echo x >> {self.hu}/.gates.jsonl"), "gates")

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

    def test_repo_bajo_tmp_no_es_desechable(self):
        self.assertTrue(str(self.repo).startswith(("/tmp", tempfile.gettempdir())))
        self.assertBlocked(self.bash_as("nexus-adversary", f"echo x > {self.repo}/app.ts"))

    def test_no_verify_para_todos(self):
        self.assertBlocked(self.bash_as("nexus-dev", "git commit --no-verify -m x"), "no-verify")
        self.assertBlocked(self.bash_as("", "git push --no-verify"), "no-verify")

    def test_dev_puede_commitear(self):
        self.assertAllowed(self.bash_as("nexus-dev", "git add -A && git commit -m x"))

    def test_agujero_conocido_sigue_documentado(self):
        # Si un dia se cierra, este test avisa que hay que corregir enforcement.md.
        self.assertAllowed(self.bash_as("nexus-adversary", "python3 -c \"open('app.ts','w')\""))


class AlTerminar(HookCase):
    def stop(self, agent):
        return self.run_hook("stop", agent_type=agent)

    def test_revisor_cambio_el_arbol(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        (self.repo / "app.ts").write_text("cambiado\n")
        self.write("ar-report.md", "STATUS: APROBADO open_blq=0\n")
        self.assertIn("arbol de git cambio", self.stop("nexus-adversary").stdout)

    def test_artefactos_no_cuentan_como_cambio(self):
        self.write("work-item.md")
        self.spawn("AR", "nexus-adversary")
        self.write("ar-report.md", "STATUS: APROBADO open_blq=0\n")
        self.assertEqual(self.stop("nexus-adversary").stdout, "")

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


if __name__ == "__main__":
    unittest.main()
