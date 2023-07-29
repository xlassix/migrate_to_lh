const os = require("os");
const axios = require("axios");
const { JsonDB } = require("node-json-db");
const { Config } = require("node-json-db/dist/lib/JsonDBConfig");
const FormData = require("form-data");
const { createReadStream, lstatSync, unlinkSync } = require("fs-extra");
const mime = require("mime-types");
const path = require("path");
const { readdir, stat } = require("fs-extra");
const record = new JsonDB(new Config(process.env.d1 || "uploadFull.json", true, true, "/"));
const record2 = new JsonDB(new Config(process.env.d1 || "upload3.json", true, true, "/"));

const BASEURL = "https://node.lighthouse.storage";
const BASE_API_URL = "https://api.lighthouse.storage";
const BASE_DIR = "./backup/";

async function walk(dir) {
  let results = [];
  const files = await readdir(dir);

  for (const file of files) {
    const filePath = `${dir}/${file}`;
    const _stat = await stat(filePath);

    if (_stat.isDirectory()) {
      results = results.concat(await walk(filePath));
    } else {
      results.push(filePath);
    }
  }

  return results;
}

const upload = async (sourcePath, token, multi, chunkSize = 2) => {
  const endpoint = BASEURL + `/api/v0/add?wrap-with-directory=${multi}`;
  const files = await walk(sourcePath);
  const mimeType = mime.lookup(sourcePath);

  // Split files array into chunks
  const chunks = [];
  for (let i = 0; i < files.length; i += chunkSize) {
    chunks.push(files.slice(i, i + chunkSize));
  }
  let count = 0;
  const results = {};

  for (const chunk of chunks) {
    const data = new FormData();

    chunk.forEach((file) => {
      //for each file stream, we need to include the correct relative file path
      data.append("file", createReadStream(file), {
        filename: path.basename(file.split("?")[0]),
      });
    });

    let response = await axios.post(endpoint, data, {
      withCredentials: true,
      maxContentLength: Infinity,
      maxBodyLength: Infinity, //this is needed to prevent axios from erroring out with large directories
      headers: {
        "Content-type": `multipart/form-data; boundary= ${data.getBoundary()}`,
        Encryption: "false",
        "Mime-Type": `${mimeType}`,
        Authorization: "Bearer " + token,
      },
    });

    if (typeof response.data === "string" && multi) {
      response.data = JSON.parse(`[${response.data.slice(0, -1)}]`.split("\n").join(","));
    } else {
      const temp = response.data.split("\n");
      response.data = JSON.parse(temp[temp.length - 2]);
    }
    // console.log(response.data);
    results[`Chunk: ${count}`] = response.data;
    console.log(`Chunk: ${count}`);
    const body = await Promise.all(
      response.data.map(async (elem) => {
        if (elem.Name == "") {
          return;
        }
        try {
          const data = await axios.post(`${BASE_API_URL}/api/lighthouse/add_cid_to_queue`, {
            cid: elem.Hash,
            name: elem.Name,
            size: elem.Size,
            publicKey,
            encryption: false,
            mimeType: mime.lookup(elem.Name.split("?")[0]),
          });
          unlinkSync(BASE_DIR + elem.Name);
          return data.data;
        } catch (e) {
          console.log(e.response.data);
        }
      })
    );
    console.log(body);
    await record.push(`/${count}`, response.data);

    count++;
  }

  return results;
};

const uploadBackup = async () => {
  try {
    const result = await upload(BASE_DIR, "", true);
    await record2.push("/", result);
    // console.log(result);
  } catch (error) {
    console.error("error", error);
  }
};

uploadBackup();
