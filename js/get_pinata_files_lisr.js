const axios = require("axios");
const { JsonDB } = require("node-json-db");
const { Config } = require("node-json-db/dist/lib/JsonDBConfig");
const record = new JsonDB(new Config(process.env.d1 || "totalFiles.json", true, true, "/"));

async function getNFTCount(bearerToken) {
  console.log("stark1");
  let offset = 0;
  let totalNFTs = offset;
  let hasMore = true;
  let count = 1;

  while (hasMore) {
    try {
      const response = await axios.get(
        `https://api.pinata.cloud/data/pinList?status=pinned&pageLimit=1000&pageOffset=${offset}`,
        {
          headers: {
            Authorization: `Bearer ${bearerToken}`,
          },
        }
      );
      totalNFTs += response.data.rows.length;
      offset += 1000;
      response.data.rows.forEach(async (file) => {
        await record.push(`/${file?.ipfs_pin_hash}`, file?.metadata?.name ?? file?.ipfs_pin_hash + ".json");
      });
      hasMore = offset < response.data.count;
      console.log("loops:", count, "\t nfs so far", totalNFTs);
      count += 1;
    } catch (error) {
      console.error("Error fetching data from Pinata:", error);
      break;
    }
  }

  return totalNFTs;
}

const bearerToken = process.env.bearerToken;
getNFTCount(bearerToken)
  .then((nftCount) => {
    console.log(`There are ${nftCount} NFTs stored on Pinata.`);
  })
  .catch((err) => console.error(err));
