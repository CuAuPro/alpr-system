import { Request, Response } from 'express';

import { AppContext } from "../app-context.js";

import { components } from '../routes/schema.js';

import { executeQuery, runQuery } from '../database/sqlite-proxy.js';
import { v4 as uuidv4 } from 'uuid';


// Module-level variable to store license plate whitelist data
var licensePlateWhitelist: components["schemas"]["LicensePlateResponse"][] = [];



// Function to initialize licensePlateWhitelist
export const initLicensePlateWhitelist = async () => {
    let response: components["schemas"]["LicensePlateResponse"][] = [];
    try {
        const query = `SELECT id, licensePlate, validFrom, validTo FROM lp_whitelist`;
        const rows: any[] = await executeQuery(query, []);

        // Transform the database rows into LicensePlateResponse objects
        response = rows.map(row => ({
            id: row.id,
            licensePlate: row.licensePlate,
            validFrom: row.validFrom,
            validTo: row.validTo
        }));
        licensePlateWhitelist = response;
        return response; // Return the data directly

    } catch (error) {
        console.error("Error fetching license plates:", error);
        throw error; // Throw error to handle it outside
    }
};


// Function to retrieve the license plate whitelist
export const getLicensePlateWhitelist = () => {
    return licensePlateWhitelist;
};



/* ----------------------------------- API ---------------------------------- */
export const healthcheck = (req: Request, res: Response) => {
    try {
        res.status(200).send("OK");
    } catch (error) {
        res.status(400).send('Error');
    }
};


// Function to get valid license plates
export const getLicensePlates = async (req: Request, res: Response) => {
    const appContext: AppContext = req.appContext;
    let response: components["schemas"]["LicensePlateResponse"][] = [];
    try {
        const query = `SELECT id, licensePlate, validFrom, validTo FROM lp_whitelist`;
        const rows: any[] = await executeQuery(query, []);

        // Transform the database rows into LicensePlateResponse objects
        response = rows.map(row => ({
            id: row.id,
            licensePlate: row.licensePlate,
            validFrom: row.validFrom,
            validTo: row.validTo
        }));

        licensePlateWhitelist = response;
        const messageString = JSON.stringify({
            eventType: "refresh-licensePlateWhitelist",
        });
        appContext.mqttProxy.event.emit("events", "alpr/refresh/lp/whitelist", messageString);

        res.status(200).send(response);
    } catch (error) {
        console.error("Error fetching license plates:", error);
        res.status(400).send(response);
    }
};

// Function to get archived license plates
export const getArchivedLicensePlates = async (req: Request, res: Response) => {
    let response: components["schemas"]["LicensePlateResponse"][] = [];
    try {
        const query = `SELECT id, licensePlate, validFrom, validTo FROM lp_whitelist_archive`;
        const rows: any[] = await executeQuery(query, []);

        // Transform the database rows into LicensePlateResponse objects
        response = rows.map(row => ({
            id: row.id,
            licensePlate: row.licensePlate,
            validFrom: row.validFrom,
            validTo: row.validTo
        }));

        res.status(200).send(response);
    } catch (error) {
        console.error("Error fetching archived license plates:", error);
        res.status(400).send(response);
    }
};

// Function to add a license plate
export const addLicensePlate = async (req: Request, res: Response) => {
    const appContext: AppContext = req.appContext;
    let response: components["schemas"]["LicensePlateCreateResponse"] = {};
    try {
        const reqData: components["schemas"]["LicensePlateRequest"] = req.body;

        const { licensePlate, validFrom, validTo } = reqData;
        const id = uuidv4(); // Generate UUID for the new license plate

        const query = `INSERT INTO lp_whitelist (id, licensePlate, validFrom, validTo) VALUES (?, ?, ?, ?)`;
        await runQuery(query, [id, licensePlate, validFrom, validTo]);
        // Append the new license plate to the licensePlateWhitelist
        const newLicensePlate = {
            id,
            licensePlate,
            validFrom,
            validTo
        };

        licensePlateWhitelist.push(newLicensePlate);
        const messageString = JSON.stringify({
            eventType: "refresh-licensePlateWhitelist",
        });
        appContext.mqttProxy.event.emit("events", "alpr/refresh/lp/whitelist", messageString);

        response.message = 'License plate added successfully';
        response.id = id;
        res.status(201).send(response);
    } catch (error) {
        response.message = 'Error adding license plate';
        console.error("Error adding license plate:", error);
        res.status(400).send(response);
    }
};

// Function to update a license plate
export const updateLicensePlate = async (req: Request, res: Response) => {
    const appContext: AppContext = req.appContext;
    let response: components["schemas"]["MessageResponse"] = {};
    try {
        const licensePlateId = req.params.id;
        const reqData: components["schemas"]["LicensePlateRequest"] = req.body;

        const { licensePlate, validFrom, validTo } = reqData;

        // Check if license plate with the given ID exists
        const checkQuery = `SELECT * FROM lp_whitelist WHERE id = ?`;
        const existingPlate = await executeQuery(checkQuery, [licensePlateId]);
        if (existingPlate.length === 0) {
            res.status(404).send({ message: 'License plate not found' });
            return;
        }

        const query = `UPDATE lp_whitelist SET licensePlate = ?, validFrom = ?, validTo = ? WHERE id = ?`;
        await runQuery(query, [licensePlate, validFrom, validTo, licensePlateId]);
        // Update the corresponding license plate in the licensePlateWhitelist
        const updatedLicensePlateIndex = licensePlateWhitelist.findIndex(lp => lp.id === licensePlateId);
        if (updatedLicensePlateIndex !== -1) {
            licensePlateWhitelist[updatedLicensePlateIndex] = {
                id: licensePlateId,
                licensePlate,
                validFrom,
                validTo
            };
        }
        const messageString = JSON.stringify({
            eventType: "refresh-licensePlateWhitelist",
        });
        appContext.mqttProxy.event.emit("events", "alpr/refresh/lp/whitelist", messageString);
        response.message = 'License plate updated successfully';
        res.status(200).send(response);
    } catch (error) {
        response.message = 'Error updating license plate';
        console.error("Error updating license plate:", error);
        res.status(400).send(response);
    }
};

// Function to delete a license plate
export const deleteLicensePlate = async (req: Request, res: Response) => {
    const appContext: AppContext = req.appContext;
    let response: components["schemas"]["MessageResponse"] = {};
    try {
        const licensePlateId = req.params.id;

        // Check if license plate with the given ID exists
        const checkQuery = `SELECT * FROM lp_whitelist WHERE id = ?`;
        const existingPlate = await executeQuery(checkQuery, [licensePlateId]);
        if (existingPlate.length === 0) {
            res.status(404).send({ message: 'License plate not found' });
            return;
        }

        const query = `DELETE FROM lp_whitelist WHERE id = ?`;
        await runQuery(query, [licensePlateId]);
        // Remove the corresponding license plate from the licensePlateWhitelist
        const deletedLicensePlateIndex = licensePlateWhitelist.findIndex(lp => lp.id === licensePlateId);
        if (deletedLicensePlateIndex !== -1) {
            licensePlateWhitelist.splice(deletedLicensePlateIndex, 1);
        }
        const messageString = JSON.stringify({
            eventType: "refresh-licensePlateWhitelist",
        });
        appContext.mqttProxy.event.emit("events", "alpr/refresh/lp/whitelist", messageString);

        response.message = 'License plate deleted successfully';
        res.status(200).send(response);
    } catch (error) {
        response.message = 'Error deleting license plate';
        console.error("Error deleting license plate:", error);
        res.status(400).send(response);
    }
};


// Function to archive expired license plates in the database
export const archiveExpiredLicensePlates = async (req: Request, res: Response) => {
    let response: components["schemas"]["MessageResponse"] = {};
    try {
        // Archive expired license plates into lp_whitelist_archive table
        const archiveQuery = `INSERT INTO 'lp_whitelist_archive' SELECT * FROM 'lp_whitelist' WHERE validTo < DATETIME('now')`;
        await runQuery(archiveQuery, []);
        console.log('Expired license plates archived successfully.');

        // Delete expired license plates from lp_whitelist table
        const deleteQuery = `DELETE FROM 'lp_whitelist' WHERE validTo < DATETIME('now')`;
        await runQuery(deleteQuery, []);
        console.log('Expired license plates deleted from lp_whitelist successfully.');

        response.message = 'Expired license plates archived successfully.';
        res.status(200).send(response);
    } catch (error) {
        console.error('Error archiving expired license plates:', error);
        res.status(400).send(response);
    }
};
