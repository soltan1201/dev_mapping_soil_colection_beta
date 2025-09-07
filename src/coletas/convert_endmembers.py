endmembers = [            
        [0.05, 0.09, 0.04, 0.61, 0.30, 0.10], #/*gv*/
        [0.14, 0.17, 0.22, 0.30, 0.55, 0.30], #/*npv*/
        [0.20, 0.30, 0.34, 0.58, 0.60, 0.58], #/*soil*/
        [0.0 , 0.0,  0.0 , 0.0 , 0.0 , 0.0 ], #/*Shade*/
        [0.90, 0.96, 0.80, 0.78, 0.72, 0.65]  #/*cloud*/ 
    ];

endmembersInt = []
for nlst in endmembers:
    print('vetor >> ', nlst)
    convert = [kk * 10000 for kk in nlst]
    endmembersInt.append(convert)


for nlst in endmembersInt:
    print(nlst)