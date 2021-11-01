import { useQuery } from "react-query";

type ResultActors = {
  actors: {
    name: string;
  }[];
};

type ResultDirectors = {
  directors: {
    name: string;
  }[];
};

type Query = [string, { query: string }];

type SelectFunction = Array<{ value: string; label: string }>;

type Genres = {
  genres: string[];
};

export const useGenres = () =>
  useQuery<Genres, unknown, SelectFunction>(
    "genres",
    async () => await (await fetch("/api/genres")).json(),
    {
      select: (data) =>
        data.genres.map((genre) => ({
          value: `${genre}`,
          label: genre,
        })),
    }
  );

export const useActors = (actorQuery: string) =>
  useQuery<ResultActors, unknown, SelectFunction, Query>(
    ["actors", { query: actorQuery }],
    async ({ queryKey }) => {
      const [_key, { query }] = queryKey;

      const response = await fetch("/api/actors", {
        method: "POST",
        body: JSON.stringify({ search: query }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      return data;
    },
    {
      select: ({ actors }) =>
        actors?.map(({ name }) => ({
          value: `${name}`,
          label: name,
        })),
    }
  );

export const useDirectors = (directorQuery: string) =>
  useQuery<ResultDirectors, unknown, SelectFunction, Query>(
    ["directors", { query: directorQuery }],
    async ({ queryKey }) => {
      const [_key, { query }] = queryKey;

      const response = await fetch("/api/directors", {
        method: "POST",
        body: JSON.stringify({ search: query }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      return data;
    },
    {
      select: ({ directors }) =>
        directors?.map(({ name }) => ({
          value: `${name}`,
          label: name,
        })),
    }
  );

type Prediction = {
  prediction: number;
};

type PredictionQuery = [
  string,
  { actors: string[]; directors: string[]; budget: number; genres: string[] }
];

export const useRatingPrediction = ({ actors, directors, budget, genres }) =>
  useQuery<Prediction, unknown, unknown, PredictionQuery>(
    ["rating", { actors, directors, budget, genres }],
    async ({ queryKey }) => {
      const [_key, { actors, directors, budget, genres }] = queryKey;
      console.log({ actors, directors, budget, genres });
      const response = await fetch("http://167.172.109.147/predict-rating", {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          people: [...actors, ...directors],
          genres: [...genres],
          budget: budget,
        }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      return data?.result;
    },
    {
      enabled: false,
    }
  );

export const useBoxOfficePrediction = ({ actors, directors, budget, genres }) =>
  useQuery<ResultDirectors, unknown, unknown, PredictionQuery>(
    ["boxoffice", { actors, directors, budget, genres }],
    async ({ queryKey }) => {
      const [_key, { actors, directors, budget, genres }] = queryKey;
      console.log({ actors, directors, budget, genres });

      const response = await fetch("http://167.172.109.147/predict-wlg", {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          people: [...actors, ...directors],
          genres: [...genres],
          budget: budget,
        }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      return data?.result;
    },
    {
      enabled: false,
    }
  );
