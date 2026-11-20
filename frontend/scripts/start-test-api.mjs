import { spawn } from "node:child_process";
import { resolve } from "node:path";
const backend = resolve(import.meta.dirname, "../../backend");
const python = resolve(backend, process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python");
const child = spawn(python, ["-m", "uvicorn", "tests.serve_api:app", "--host", "127.0.0.1", "--port", "8000"], { cwd: backend, stdio: "inherit" });
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => child.kill(signal));
child.on("exit", (code) => process.exit(code ?? 1));
