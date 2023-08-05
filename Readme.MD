# Guide to Pinata Migration and Data Validation

This document provides a step-by-step guide to migrate data and perform checks with Piñata.

## Prerequisites

Before you start, ensure you have Node.js and NPM/Yarn installed on your system.

## Step 1: Set Environment Variables

Environment variables provide a way to influence the behavior of software on your system. They consist of names with corresponding values and allow applications to know something about the environment in which they are running.

1. Create a `.env` file at the root of this project. You can use the `.env.example` file as a reference.

2. Update the `.env` file with your data. Ensure that the `LIGHTHOUSE_TOKEN` and `PINATA_JWT` variables are correctly set. These are essential for the successful execution of the migration and validation scripts.

## Step 2: Install Dependencies

Dependencies are external modules that this project relies on to function correctly.

To install these dependencies, navigate to the project directory and run one of the following commands, depending on your package manager:

```bash
npm install
```
or
```bash
yarn install
```

## Step 3: Generate JSON File for CID Mapping of Piñata Files

The next step is to create a JSON file that maps the Content Identifiers (CIDs) to the Piñata files.

Execute the following command in your terminal:

```bash
node js/get_pinata_files.js
```

This will generate the JSON file with the necessary mappings.

## Step 4: Execute Validation and Checks

Now you can run the validation script. It verifies the data consistency and performs necessary checks. If it discovers any data that hasn't been uploaded to Lighthouse, the script will attempt to upload it.

Use the following command to run the script:

```bash
node js/validate_upload.js
```

You can run this script as many times as needed.

**Note**: Always ensure your environment variables are correctly set before executing the scripts. Any changes in the `.env` file will necessitate a script re-run.