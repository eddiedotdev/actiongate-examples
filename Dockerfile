FROM node:22-alpine

ENV ACTIONGATE_BASE_URL=https://api.actiongate.xyz
ENV PAYTO_ADDRESS=0x0000000000000000000000000000000000000000

RUN npm install -g actiongate-mcp

EXPOSE 3000

CMD ["actiongate-mcp"]
