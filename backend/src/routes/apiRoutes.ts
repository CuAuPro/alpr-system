import Express from 'express';
import { healthcheck, addLicensePlate, updateLicensePlate, deleteLicensePlate, archiveExpiredLicensePlates, getLicensePlates, getArchivedLicensePlates } from '../controllers/apiController.js';

export default class ApiRoutes {
  public router: Express.Router;
  //private upload: multer.Multer;

  constructor() {

    //this.upload = multer({ storage: storage });

    this.router = Express.Router();
    this.router.use(
      (
        req: Express.Request,
        res: Express.Response,
        next: Express.NextFunction
      ) => {
        console.log("/api, Time: ", Date.now());
        next();
      }
    );


    this.router.get('/healthcheck', healthcheck);

    // License Plates
    this.router.get('/license-plates', getLicensePlates); // Get valid license plates
    this.router.post('/license-plates', addLicensePlate); // Add a new license plate
    this.router.put('/license-plates/:id', updateLicensePlate); // Update a license plate
    this.router.delete('/license-plates/:id', deleteLicensePlate); // Delete a license plate
    this.router.post('/license-plates/archive', archiveExpiredLicensePlates); // Archive expired license plates
    this.router.get('/license-plates/archive', getArchivedLicensePlates); // Get archived license plates

  }
}

