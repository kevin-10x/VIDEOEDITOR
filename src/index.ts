import { Container, WorkerEntrypoint } from "cloudflare:workers";

interface Env {
  MY_CONTAINER: DurableObjectNamespace;
}

export default class extends WorkerEntrypoint<Env> {
  async fetch(request: Request): Promise<Response> {
    const id = this.env.MY_CONTAINER.newUniqueId();
    const stub = this.env.MY_CONTAINER.get(id);

    return stub.fetch(request);
  }
}

export class MyContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";

  onError(error: unknown): Response {
    console.error("Container error:", error);
    return new Response("Container error", { status: 500 });
  }
}
