import { basePath } from '../base-path.js';
import path from 'path';
import sqlite3 from 'sqlite3';


const dbDir = path.join(basePath, 'database');
const dbFile = path.join(dbDir, 'alpr.db')

// Initialize SQLite database
const db = new sqlite3.Database(dbFile);


export const executeQuery = async (query: string, params: any[]): Promise<any> => {
    return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
            if (err) {
                reject(err);
            } else {
                resolve(rows);
            }
        });
    });
};

export const runQuery = async (query: string, params: any[]): Promise<void> => {
    return new Promise((resolve, reject) => {
        db.run(query, params, (err) => {
            if (err) {
                reject(err);
            } else {
                resolve();
            }
        });
    });
};
