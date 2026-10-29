import test from 'node:test';
import assert from 'node:assert/strict';
import handler from '../api/keepalive.js';

function response() {
  return {
    statusCode: 200, headers: {},
    setHeader(key,value){this.headers[key]=value;},
    status(code){this.statusCode=code;return this;},
    json(value){this.body=value;return this;}
  };
}
async function invoke(method,authorization,body) {
  const res=response();
  await handler({method,headers:authorization?{authorization}:{},body},res);
  return res;
}
test('rejects GET without exposing state mutation',async()=>{
  const res=await invoke('GET');
  assert.equal(res.statusCode,405);
});
test('rejects requests when credentials are unavailable',async()=>{
  const previous=process.env.KEEPALIVE_ADMIN_KEY;
  const token=process.env.KEEPALIVE_GITHUB_TOKEN;
  delete process.env.KEEPALIVE_ADMIN_KEY;
  delete process.env.KEEPALIVE_GITHUB_TOKEN;
  try { assert.equal((await invoke('POST')).statusCode,503); }
  finally {
    if(previous===undefined)delete process.env.KEEPALIVE_ADMIN_KEY;
    else process.env.KEEPALIVE_ADMIN_KEY=previous;
    if(token===undefined)delete process.env.KEEPALIVE_GITHUB_TOKEN;
    else process.env.KEEPALIVE_GITHUB_TOKEN=token;
  }
});
test('rejects missing and incorrect authorization without calling GitHub',async()=>{
  process.env.KEEPALIVE_ADMIN_KEY='test-only-secret';
  process.env.KEEPALIVE_GITHUB_TOKEN='test-only-token';
  const original=globalThis.fetch;
  let called=false;
  globalThis.fetch=async()=>{called=true;throw Error('should not fetch');};
  try {
    assert.equal((await invoke('POST',null,{enabled:false})).statusCode,401);
    assert.equal((await invoke('POST','Bearer wrong',{enabled:false})).statusCode,401);
    assert.equal(called,false);
  } finally {globalThis.fetch=original;delete process.env.KEEPALIVE_ADMIN_KEY;delete process.env.KEEPALIVE_GITHUB_TOKEN;}
});
test('rejects non-boolean state without calling GitHub',async()=>{
  process.env.KEEPALIVE_ADMIN_KEY='test-only-secret';
  process.env.KEEPALIVE_GITHUB_TOKEN='test-only-token';
  const original=globalThis.fetch;
  let called=false;
  globalThis.fetch=async()=>{called=true;throw Error('should not fetch');};
  try {
    assert.equal((await invoke('POST','Bearer test-only-secret',{enabled:'false'})).statusCode,400);
    assert.equal(called,false);
  } finally {globalThis.fetch=original;delete process.env.KEEPALIVE_ADMIN_KEY;delete process.env.KEEPALIVE_GITHUB_TOKEN;}
});
