const { upload } = require("@lighthouse-web3/sdk");

const uploadBackup = async () => {
  try {
    const result = await upload("./backup", API_KEY, true);
    console.log(result);
  } catch (error) {
    console.error("error", error);
  }
};

uploadBackup();
