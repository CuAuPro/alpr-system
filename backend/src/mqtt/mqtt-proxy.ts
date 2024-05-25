import { EventEmitter } from "events";
import mqtt, { IClientOptions } from "mqtt";
import * as fs from "fs";
import * as path from "path";
import { basePath, __dirname, __filename } from '../base-path.js';

export default class MqttProxy {
  public event: EventEmitter = new EventEmitter();
  private mqttHost: string;
  private mqttSubToTopics: string[] | string;
  private mqttSSL: boolean;
  private username?: string;
  private password?: string;
  public mqttClient: mqtt.MqttClient;

  /**
   * Connect to MQTT broker
   * @param mqttHost - MQTT broker host
   * @param mqttSubToTopics - Topics to subscribe to
   * @param username - Username for authentication
   * @param password - Password for authentication
   * @param mqttSSL - Use SSL/TLS if true
   */
  constructor(
    mqttHost: string,
    mqttSubToTopics?: string | string[],
    username?: string,
    password?: string,
    mqttSSL?: boolean
  ) {
    this.mqttHost = mqttHost;
    this.mqttSubToTopics = mqttSubToTopics || [];
    this.username = username;
    this.password = password;
    this.mqttSSL = mqttSSL || false;

    console.log("Initializing MQTT Proxy");

    this.connectToMqtt();
  }

  /**
   * Create MQTT connection options
   * @returns MQTT connection options
   */
  private createMqttOptions(): IClientOptions {
    let options: IClientOptions = {
      username: this.username,
      password: this.password,
    };

    if (this.mqttSSL) {
      try {
        const key = fs.readFileSync(path.join(__dirname, "../certs/databus/databus-backend.key"));
        const cert = fs.readFileSync(path.join(__dirname, "../certs/databus/databus-backend.crt"));
        const ca = fs.readFileSync(path.join(__dirname, "../certs/databus/ca.crt"));

        options = {
          ...options,
          key,
          cert,
          ca,
          rejectUnauthorized: false,
        };
      } catch (error) {
        console.error("Error loading SSL certificates:", error.message);
      }
    }

    return options;
  }

  /**
   * Connect to the MQTT broker and set up event listeners
   */
  private connectToMqtt(): void {
    const options = this.createMqttOptions();
    //const protocol = this.mqttSSL ? "mqtts" : "mqtt";
    const protocol = "mqtt";
    const url = `${protocol}://${this.mqttHost}`;

    this.mqttClient = mqtt.connect(url, options);

    this.mqttClient.on("connect", () => {
      console.log(`Connected to ${this.mqttHost}`);
      if (this.mqttSubToTopics.length > 0) {
        console.log(`Subscribed to ${this.mqttSubToTopics}`);
        this.mqttClient.subscribe(this.mqttSubToTopics);
      }
    });

    this.mqttClient.on("message", (topic: string, message: Buffer) => {
      this.handleMessage(topic, message);
    });

    this.mqttClient.on("error", (error: Error) => {
      console.error("MQTT Client Error:", error.message);
    });
  }

  /**
   * Handle incoming MQTT messages
   * @param topic - The topic of the message
   * @param message - The message payload
   */
  private handleMessage(topic: string, message: Buffer): void {
    try {
      const messageString = message.toString();
      //console.log(`Message received from topic ${topic}: ${messageString}`);
      this.event.emit("events", topic, messageString);
    } catch (error) {
      console.error("Error handling message:", error.message);
    }
  }
}
