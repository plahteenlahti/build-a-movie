import csv from "csv-parser";
import fs from "fs";
import getConfig from "next/config";
import path from "path";

export default function handler(req, res) {
  res.status(200).json({
    genres: [
      "Comedy",
      "Drama",
      "News",
      "Crime",
      "Talk-Show",
      "Action",
      "Adult",
      "Thriller",
      "Sport",
      "Mystery",
      "Romance",
      "Sci-Fi",
      "Film-Noir",
      "Reality-TV",
      "Biography",
      "War",
      "Fantasy",
      "Musical",
      "History",
      "Animation",
      "Documentary",
      "Music",
      "Family",
      "Horror",
      "Western",
      "Game-Show",
      "Short",
      "Adventure",
    ],
  });
}
