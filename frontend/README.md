# Frontend

This directory contains the frontend code for the Automatic License Plate Recognition System Management. It is built with Angular.

| ![](/docs/img/frontend-welcome.jpeg) |
|:--:| 
| ALPR Manager – Welcome. |

| ![](/docs/img/frontend-signin.jpeg) |
|:--:| 
| ALPR Manager – Sign In. |


| ![](/docs/img/frontend-dashboard.jpeg) |
|:--:| 
| ALPR Manager – UI. |


| ![](/docs/img/frontend-dashboard-addlp.jpeg) |
|:--:| 
| ALPR Manager – Add License Plate. |

## Features

- User authentication
- Responsive design
- Data visualization

## Setup Instructions

### Prerequisites

- Node.js
- Angular CLI

### API Types
To generate TypeScript API types from the Swagger API specification, follow these steps:



1. Install the required package:
```bash
npm install @hey-api/openapi-ts --save-dev

```
2. Convert Swagger YAML (from `backend`) to JSON and copy it into the `frontend`.

You can do it automatically:

```bash
npm install -g yamljs
```

```bash
yaml2json ..\backend\src\routes\swagger.yaml > .\src\app\rest-api\swagger.json
```


3. Generate TypeScript API types:
```bash
./node_modules/.bin/openapi-ts -i .\src\app\rest-api\swagger.json -o .\src\app\rest-api\ -c angular
```


### Installation

1. Install dependencies:
```bash
npm install
```

2. Build the project (optional):

```bash
ng build --configuration=production
```


### Running the Application

Start the frontend server:

```bash
ng serve
```

The application will run on `http://localhost:4200`.

## Acknowledgements

This repository is based on the following source: https://github.com/azouaoui-med/lightning-admin-angular.


## License 

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.