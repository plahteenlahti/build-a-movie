import { useQuery } from "react-query";

export const useDirectors = () =>
  useQuery(
    ["actors", { query: actorQuery }],
    async ({ queryKey }) => {
      const [_key, { query }] = queryKey;

      const response = await fetch("/api/actors", {
        method: "POST",
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log("response", data);
      return data;
    },
    {
      select: ({ data }) =>
        data.actors.map(({ name }) => ({
          value: `${name}`.toLowerCase(),
          label: name,
        })),
    }
  );
