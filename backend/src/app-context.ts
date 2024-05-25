import { components } from "./routes/schema.js";
import MqttProxy from "./mqtt/mqtt-proxy.js";

export interface AppContext {
    mqttProxy: MqttProxy;
}
