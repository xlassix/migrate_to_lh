const async = require("async");
const os = require("os");
const axios = require("axios");
const { JsonDB } = require("node-json-db");
const { Config } = require("node-json-db/dist/lib/JsonDBConfig");
const mime = require("mime-types");
const FormData = require("form-data");
const dotenv = require("dotenv");
const path = require("path");
const { readdir, stat, access, createReadStream, readFileSync } = require("fs-extra");
const record = new JsonDB(new Config(process.env.d1 || "totalFiles_lh.json", true, true, "/"));

const BASE_API_URL = "https://api.lighthouse.storage";
dotenv.config();

const token = process.env.LIGHTHOUSE_TOKEN;

function readJson(filepath) {
  const rawData = readFileSync(filepath, "utf-8");
  const jsonData = JSON.parse(rawData);

  if (typeof jsonData !== "object" || Array.isArray(jsonData)) {
    throw new Error("JSON data should be an object");
  }

  return jsonData;
}

async function download_from_ipfs(ipfs_hash, filename) {
  const data = new FormData();
  const endpoint = "https://node.lighthouse.storage" + `/api/v0/add`;
  const mimeType = mime.lookup(filename);
  //   if (!fileExists(`./backup/${filename}`)) {

  const gateway_urls = ["https://ipfs.io/ipfs/", "https://gateway.pinata.cloud/ipfs/"];
  for (const url of gateway_urls) {
    try {
      const response = await axios.get(url + ipfs_hash, { responseType: "arraybuffer" });
      if (response.status === 200) {
        data.append("file", response.data, {
          filename: path.basename(filename.split("?")[0]),
        });
        let _response = await axios.post(endpoint, data, {
          withCredentials: true,
          maxContentLength: Infinity,
          maxBodyLength: Infinity,
          headers: {
            "Content-type": `multipart/form-data; boundary= ${data.getBoundary()}`,
            Encryption: "false",
            "Mime-Type": `${mimeType}`,
            Authorization: "Bearer " + token,
          },
        });
        return [response.data, filename];
      }
    } catch (error) {
      console.log(error.message);
      continue;
    }
  }

  return null;
}

async function processJsonEntry(entryValue) {
  // Process the entry as needed
  try {
    const response = await axios.get(`${BASE_API_URL}/api/lighthouse/file_info?cid=${entryValue[0]}`);
    console.log(`Processed ${JSON.stringify(response.data)}`);
    await record.push(`/${entryValue[0]}`, entryValue[1]);
  } catch (e) {
    if (e.response?.status === 404) {
      const res = await download_from_ipfs(entryValue[0], entryValue[1]);
      console.log(`Uploaded: ${entryValue[0]}`);
    } else {
      console.log(`error:`, e);
    }
  }
  return Promise.resolve(); // Return a promise, as `async.eachLimit` expects async functions to return
}

async function main() {
  // const jsonData = await record.getData("/");
  const jsonData = readJson("./Pinata_totalFiles.json");
  const entries = Object.entries(jsonData); //.splice(100000);
  const parallelLimit = 5; //os.cpus().length; // Set the limit to the number of CPU cores

  async.eachLimit(
    entries,
    parallelLimit,
    async (entry) => {
      await processJsonEntry(entry);
    },
    (err) => {
      console.log(err);
      if (err) {
        console.error("An entry failed to process:", err);
      } else {
        console.log("All entries processed.");
      }
    }
  );
}

main();
