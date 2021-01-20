n = 3
K = 4
DIS_C2BS = [0.46089178 0.35314213 0.49883177]
GAIN_C2BS = zeros(n,K);
G1 = 10^(-2);
alpha1 = 3; 
for j=1:n
    beta1 = exprnd(1,1,K); 
    gamma1 = lognrnd(0,10^(0.8),1,K);  
    GAIN_C2BS(j,:) = G1*(beta1.*(gamma1)*DIS_C2BS(1,j)^(-alpha1));
end

GAIN_C2BS

for j=1:n
    for k = 1:K
        if GAIN_C2BS(j,k) > 1e-4
            GAIN_C2BS(j,k) = 1e-8 + (9e-12-1e-12).*rand(1);
        end
    end
end

GAIN_C2BS

lambda = 1;
fast_fading = -(1/lambda)*log(1-rand);

fast_fading

std=8;
mu=1;
sx=sqrt(log(std^2/mu^2+1));
mx=log(mu)-sx^2/2;
X=exp(mx+sx*randn);
slow_fading = X;

slow_fading

alpha=4;
K=10^(-2);

d_d_pair = 0.48988192*1000;

gain_d_pair = K*fast_fading*slow_fading*d_d_pair^(-alpha);

gain_d_pair