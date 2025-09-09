import api from "./api"

/**
 * Fetches an image from the backend API.
 *
 * - Uses the pre-configured Axios instance (`api`) to make the request.
 * - Sends a GET request to `/image` endpoint.
 * - Returns only the response data (`res.data`) instead of the entire Axios response object.
 *
 * @async
 * @function getImage
 * @returns {Promise<any>} The data returned from the `/image` endpoint.
 *
 * Example usage:
 * const imageData = await getImage();
 * console.log(imageData);
 */
export const getImage = async () => {
  const res = await api.get("/image");
  return res.data; // extract only data of the payload
};
