# Pinata Migration and Check

## Step 1

Set Environment Variables

- Make a `.env` file in the directory of this project using `.env.example`
  NB the value `LIGHTHOUSE_TOKEN` and `PINATA_JWT` are crucial

## Step 2

Install Dependencies

- run `npm install` or `yarn install`

## Step 3

Create Json storing CID mapping for Pinata Files
run:

```
node js/get_pinata_files.js
```

## Step 4

Run Validator and Checks
FYI: you can run this script multiple times

```
node js/validate_upload.js
```
