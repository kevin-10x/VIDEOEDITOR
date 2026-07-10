import { Container, getContainer } from "@cloudflare/containers";

interface Env {
  MY_CONTAINER: DurableObjectNamespace;
}

export class MyContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";

  override onStart() {
    console.log("Video Editor container started");
  }

  override onStop() {
    console.log("Video Editor container stopped");
  }

  override onError(error: unknown) {
    console.error("Container error:", error);
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return getContainer(env.MY_CONTAINER, "video-editor").fetch(request);
  },
};
