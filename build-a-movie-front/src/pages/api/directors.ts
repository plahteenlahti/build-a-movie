async function fetchGraphQL(query: string) {
  return fetch(`https://meet-spider-88.hasura.app/v1/graphql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-hasura-admin-secret": `${process.env.HASURA_TOKEN}`,
    },
    body: JSON.stringify({ query }),
  }).then((response) => response.json());
}

export default async function handler(req, res) {
  const query = await req.body;
  console.log(query.query);
  const result = await fetchGraphQL(`query {
      directors(limit: 100, where: {name: {_ilike: "%${query.query ?? ""}%"}}) {
        name
      }
    }`);
  res.status(200).json({ ...result });
}
