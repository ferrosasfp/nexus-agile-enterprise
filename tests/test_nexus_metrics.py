#!/usr/bin/env python3
"""Pruebas del script de metricas con transcripts sinteticos, con la forma de los de Claude Code."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / ".claude/skills/nexus-agile/scripts/nexus_metrics.py"


def line(**entry):
    return json.dumps(entry)


def assistant(msg_id, ts, usage, tools=()):
    content = [{"type": "tool_use", "id": t[0], "name": t[1], "input": {}} for t in tools]
    return line(type="assistant", timestamp=ts, message={"id": msg_id, "role": "assistant", "model": "m", "usage": usage, "content": content})


def result(tool_id, ts, text, error=False):
    return line(type="user", timestamp=ts, message={"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tool_id, "is_error": error, "content": text}]})


class Metricas(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.session = self.tmp / "s1"
        (self.session / "subagents").mkdir(parents=True)
        self.hu = self.tmp / "doc/sdd/001-x"
        self.hu.mkdir(parents=True)
        usage1 = {"input_tokens": 10, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 5, "output_tokens": 20}
        usage2 = {"input_tokens": 2, "cache_read_input_tokens": 900, "cache_creation_input_tokens": 50, "output_tokens": 48}
        rows = [
            line(type="user", timestamp="2026-11-02T10:00:00Z", message={"role": "user", "content": f"RUTAS: x\nFASE: AR\nHU_DIR: {self.hu}\nrevisa"}),
            assistant("m1", "2026-11-02T10:00:10Z", usage1, tools=[("t1", "Bash"), ("t2", "Read")]),
            assistant("m1", "2026-11-02T10:00:10Z", usage1, tools=[("t1", "Bash")]),  # la misma respuesta partida en dos lineas
            result("t1", "2026-11-02T10:00:20Z", "PreToolUse:Bash hook error: NEXUS GATE: nexus-adversary no escribe", error=True),
            result("t2", "2026-11-02T10:00:21Z", "el reporte anterior cita NEXUS GATE: algo"),  # una cita no es un bloqueo
            assistant("m2", "2026-11-02T10:01:40Z", usage2),
            # una segunda vuelta, una hora despues: la espera no es tiempo activo
            line(type="user", timestamp="2026-11-02T11:01:40Z", message={"role": "user", "content": "sigue"}),
            assistant("m3", "2026-11-02T11:01:50Z", usage1),
        ]
        (self.session / "subagents/agent-a1.jsonl").write_text("\n".join(rows) + "\n")
        (self.session / "subagents/agent-a1.meta.json").write_text(json.dumps({"agentType": "nexus-agile:nexus-adversary", "description": "AR"}))
        other = [line(type="user", timestamp="2026-11-02T11:00:00Z", message={"role": "user", "content": "FASE: F1\nHU_DIR: /otra\nx"}),
                 assistant("m9", "2026-11-02T11:00:05Z", usage1)]
        (self.session / "subagents/agent-b2.jsonl").write_text("\n".join(other) + "\n")
        (self.session.with_suffix(".jsonl")).write_text(result("o1", "2026-11-02T09:00:00Z", "NEXUS GATE: los gates solo los registra el hook", error=True) + "\n")
        (self.hu / ".gates.jsonl").write_text('{"gate": "HU_APPROVED"}\n{"gate": "VIOLATION", "by": "nexus-dev", "files": ["/x/sdd.md"]}\n')

    def run_script(self, *args):
        out = subprocess.run([sys.executable, "-I", str(SCRIPT), "--session", str(self.session), *args], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def test_cuenta_como_el_harness(self):
        data = json.loads(self.run_script("--hu-dir", str(self.hu), "--json"))
        self.assertEqual(data["totals"]["launches"], 1)
        agent = data["agents"][0]
        self.assertEqual(agent["tokens"], 135)  # contexto final del ultimo mensaje (m3)
        self.assertEqual(agent["seconds"], 110)  # 100 s de la primera vuelta + 10 s de la segunda, sin la hora de espera
        self.assertEqual(agent["span_seconds"], 3710)
        self.assertEqual(agent["rounds"], 2)
        self.assertEqual(agent["processed"], 135 + 1000 + 135)
        self.assertEqual(agent["tool_uses"], 2)  # sin contar dos veces la respuesta partida
        self.assertEqual(agent["usage"]["output"], 88)
        self.assertEqual(len(agent["hook_blocks"]), 1)  # la cita del reporte no cuenta
        self.assertEqual(len(data["orchestrator_hook_blocks"]), 1)
        self.assertEqual(data["gates"]["counts"], {"HU_APPROVED": 1, "VIOLATION": 1})

    def test_sin_filtro_cuenta_todas_las_hus(self):
        data = json.loads(self.run_script("--json"))
        self.assertEqual(data["totals"]["launches"], 2)

    def test_busca_las_sesiones_de_la_hu(self):
        projects = self.tmp / "projects"
        (projects / "-repo").mkdir(parents=True)
        shutil.move(str(self.session), projects / "-repo" / "s1")
        shutil.move(str(self.session.with_suffix(".jsonl")), projects / "-repo" / "s1.jsonl")
        out = subprocess.run([sys.executable, "-I", str(SCRIPT), "--hu-dir", str(self.hu), "--projects", str(projects), "--json"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        data = json.loads(out.stdout)
        self.assertEqual((data["totals"]["launches"], data["totals"]["hook_blocks"]), (1, 2))

    def test_tabla_legible(self):
        out = self.run_script("--hu-dir", str(self.hu))
        self.assertIn("| 1 | AR | nexus-adversary |", out)
        self.assertIn("VIOLATION de nexus-dev: sdd.md", out)


if __name__ == "__main__":
    unittest.main()
