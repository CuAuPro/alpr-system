// Add the following code to the startup process
/**
 * Module dependencies.
 */
import App from "./app.js";
import { AppContext } from "./app-context.js";
import terminate from "./terminate.js";
import MqttProxy from './mqtt/mqtt-proxy.js';  // Adjust the path as necessary


// Define your MQTT connection parameters
const mqttHost = process.env.MQTT_BROKER || 'localhost:8883'; // Use MQTT_BROKER if set, otherwise default to 'localhost:8883'

const mqttSubToTopics = ['admin/test', 'alpr/ramp/req']; // Array of topics to subscribe to
const username = process.env.MQTT_USERNAME !== undefined ? process.env.MQTT_USERNAME : '';
const password = process.env.MQTT_PASSWORD !== undefined ? process.env.MQTT_PASSWORD : '';
const mqttSSL = process.env.MQTT_SSL !== undefined ? process.env.MQTT_SSL === 'true' : true; // Default to true if not specified, convert string to boolean

// Create an instance of MqttProxy
const mqttProxy = new MqttProxy(mqttHost, mqttSubToTopics, username, password, mqttSSL);

/**
 * Express http server
 */
const context: AppContext = {
  mqttProxy: mqttProxy
};

const PORT = parseInt(process.env.PORT) || 443;
const app = new App(context, PORT);
app.start();


/**
 * Error handler
 */
const exitHandler = terminate(app.server, {
  coredump: false,
  timeout: 500,
});

process.on("uncaughtException", exitHandler(1, "Unexpected Error"));
process.on("unhandledRejection", exitHandler(1, "Unhandled Promise"));
process.on("SIGTERM", exitHandler(0, "SIGTERM"));
process.on("SIGINT", exitHandler(0, "SIGINT"));
