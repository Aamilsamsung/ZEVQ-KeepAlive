import crypto from 'node:crypto';
const OWNER='Aamilsamsung', REPO='ZEVQ-KeepAlive', PATH='keepalive.json';
function equal(a,b){const x=crypto.createHash('sha256').update(a).digest(),y=crypto.createHash('sha256').update(b).digest();return crypto.timingSafeEqual(x,y)}
export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST')return res.status(405).json({error:'Method not allowed'});
  const secret=process.env.KEEPALIVE_ADMIN_KEY, token=process.env.KEEPALIVE_GITHUB_TOKEN;
  if(!secret||!token)return res.status(503).json({error:'Server credentials not configured'});
  const auth=req.headers.authorization||'';
  if(!auth.startsWith('Bearer ')||!equal(auth.slice(7),secret))return res.status(401).json({error:'Unauthorized'});
  if(typeof req.body?.enabled!=='boolean')return res.status(400).json({error:'enabled must be boolean'});
  const base='https://api.github.com/repos/'+OWNER+'/'+REPO+'/contents/'+PATH;
  const headers={Authorization:'Bearer '+token,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'};
  try{
    for(let attempt=0;attempt<3;attempt++){
      const get=await fetch(base+'?ref=main',{headers,cache:'no-store'});
      if(!get.ok)return res.status(502).json({error:'Cannot read state from GitHub'});
      const file=await get.json();
      const content=Buffer.from(JSON.stringify({enabled:req.body.enabled,updatedAt:new Date().toISOString()})+'\n').toString('base64');
      const put=await fetch(base,{method:'PUT',headers,body:JSON.stringify({message:req.body.enabled?'Enable background KeepAlive':'Disable background KeepAlive',content,sha:file.sha,branch:'main'})});
      if(put.ok)return res.status(200).json({enabled:req.body.enabled});
      if(put.status!==409&&put.status!==422)return res.status(502).json({error:'GitHub refused state update'});
    }
    return res.status(409).json({error:'Concurrent update; retry'});
  }catch{return res.status(502).json({error:'GitHub connection unavailable'})}
}
