/**
 * Module dependencies.
 */
import * as path from "path"

import Express, { Request, Response } from 'express';
import * as http from "http";
import * as https from "https";

import * as fs from "fs";
import cors from "cors";
import session from "express-session";
import cookieParser from "cookie-parser";
import { AppContext } from "./app-context.js";

import YAML from 'yamljs';
import { basePath, __dirname, __filename } from './base-path.js';


import swaggerUi from 'swagger-ui-express';
import authMiddleware from "./middleware/authMiddleware.js";

import AuthRoutes from './routes/authRoutes.js';
import ApiRoutes from './routes/apiRoutes.js';
import MqttProxy from "./mqtt/mqtt-proxy.js";
import { components } from "./routes/schema.js";
import { getLicensePlateWhitelist, initLicensePlateWhitelist } from "./controllers/apiController.js";


export default class App {
  private expressApplication: Express.Application;
  private authRoutes: any;
  private apiRoutes: any;
  public server;
  private port;
  private mqttProxy: MqttProxy;
  private appContext: AppContext;
  private licensePlateWhitelist: components["schemas"]["LicensePlateResponse"][];

  constructor(appContext: AppContext, port: number) {
    this.port = port;
    this.authRoutes = new AuthRoutes();
    this.apiRoutes = new ApiRoutes();
    this.expressApplication = Express();
    this.appContext = appContext;
    this.mqttProxy = this.appContext.mqttProxy; // Save mqttProxy instance
    this.licensePlateWhitelist = [];

    // Create HTTP server for RSS
    this.server = http.createServer(this.expressApplication);

    const swaggerDocument = YAML.load(path.join(__dirname, './routes/swagger.yaml'));

    this.expressApplication.use(
      session({
        secret: "CHANGEME",
        resave: false,
        saveUninitialized: true,
      })
    );

    // Add context
    this.expressApplication.use((req: Request, res: Response, next) => {
      req.appContext = appContext;
      next();
    });

    // Use the cors middleware
    this.expressApplication.use(cors({
      origin: [
        "https://localhost",
        "https://frontend",

      ],
      methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
      credentials: true,
      optionsSuccessStatus: 204,
      allowedHeaders: ["Origin", "X-Requested-With", "Content-Type", "Accept", "Authorization", "Access-Control-Allow-Origin"],
    }));

    // Body parser (req.body)
    this.expressApplication.use(Express.json());
    this.expressApplication.use(Express.urlencoded({ extended: false }));

    // Add cookie parser
    this.expressApplication.use(cookieParser());

    // Static / public folder
    const publicHome =
      process.env.PUBLIC_HOME === null || process.env.PUBLIC_HOME === undefined
        ? "public"
        : process.env.PUBLIC_HOME;
    this.expressApplication.use(
      Express.static(path.join(__dirname, publicHome))
    );

    // Map routes
    //this.expressApplication.use("/api", this.api.router);

    this.expressApplication.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
    this.expressApplication.use('/auth', this.authRoutes.router);

    // Apply authentication middleware to /api routes
    this.expressApplication.use('/api', authMiddleware);
    this.expressApplication.use('/api', this.apiRoutes.router);

    // this.expressApplication.use(Express.static(path.join(__dirname, '../../frontend/dist/frontend/browser')));

    // this.expressApplication.get('*', (req, res) => {
    //   res.sendFile(path.join(__dirname, '../../frontend/dist/frontend/browser/index.html'));
    // });

    // Example of using mqttProxy within the App class
    this.setupMqttHandlers();

  }

  public async start() {
    this.licensePlateWhitelist =  await initLicensePlateWhitelist();
    // Listen on provided port, on all network interfaces.
    this.server.listen(this.port);
    this.server.on("error", (error: { syscall: string; code: any }) => {
      if (error.syscall !== "listen") {
        throw error;
      }

      const bind =
        typeof this.port === "string"
          ? `Pipe ${this.port}`
          : `Port ${this.port}`;

      // handle specific listen errors with friendly messages
      switch (error.code) {
        case "EACCES":
          console.error(`${bind} requires elevated privileges`);
          process.exit(1);
          break;
        case "EADDRINUSE":
          console.error(`${bind} is already in use`);
          process.exit(1);
          break;
        default:
          throw error;
      }
    });
    this.server.on("listening", () => {
      App.bind(this);
      const addr = this.server.address();
      const bind =
        typeof addr === "string" ? `pipe ${addr}` : `port ${addr.port}`;
      //console.log(`Listening on ${bind}`);
      console.log(`Server is running on https://localhost:${this.port}`);
    });
  }
  
  private setupMqttHandlers() {
    // Handle events emitted by mqttProxy
    this.mqttProxy.event.on('events', async (topic: string, message: string) => {
        //console.log(`Received message on topic ${topic}: ${message}`);
        try {
            if (topic === 'alpr/refresh/lp/whitelist') {
                //console.log(message);
                this.licensePlateWhitelist = await getLicensePlateWhitelist();
                //console.log(this.licensePlateWhitelist);
            } else if (topic === 'alpr/ramp/req') {
                // Parse the message to extract the license plate
                const parsedMessage = JSON.parse(message);
                const licensePlate = parsedMessage.licensePlate;

                // Find if licensePlate is in licensePlateWhitelist and valid for today
                const validLicensePlate = this.licensePlateWhitelist.find(lp => {
                    return lp.licensePlate === licensePlate && this.isDateValid(lp.validFrom, lp.validTo);
                });

                if (validLicensePlate) {
                    console.log(`License plate ${licensePlate} is valid.`);
                    const messageString = JSON.stringify({
                        eventType: "command-open-ramp",
                        details: "open-ramp",
                        value: 1
                    });
                    this.mqttProxy.mqttClient.publish("alpr/ramp/cmd", messageString);
                    // Additional logic here if needed
                } else {
                    console.log(`License plate ${licensePlate} is not valid or not found in the whitelist.`);
                    // Additional logic here if needed
                }
            }
        } catch (error) {
            console.error("Error handling MQTT event:", error);
            // Handle error here
        }
    });
  }

  // Helper function to ensure date consistency
  toLocalDateString = (dateString: string): string => {
    const date = new Date(dateString);
    // Adjust for time zone offset to keep the local date the same in UTC
    const adjustedDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
    return adjustedDate.toISOString().split('T')[0];
  };

  // Function to check if a date falls within a range (inclusive)
  private isDateValid(validFrom: string, validTo: string): boolean {
    const currentDateString = this.toLocalDateString(new Date().toISOString());
    const validFromDateString = this.toLocalDateString(validFrom);
    const validToDateString = this.toLocalDateString(validTo);

    return currentDateString >= validFromDateString && currentDateString <= validToDateString;
}
}
