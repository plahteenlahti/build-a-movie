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
  const body = await req.body;
  const query = JSON.parse(body);

  const result = await fetchGraphQL(`query {
      directors(limit: 100, where: {name: {_ilike: "%${
        query.search ?? ""
      }%"}}) {
        name
      }
    }`);
  res.status(200).json({ ...result?.data });
}
