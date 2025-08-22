def format_to_edi_x12(inputs: dict):
    bundle = inputs["bundle"]
    context = inputs["context"]

    edi = f"""ISA*00*...*GS*HC*SUBMITTER*PAYER*20240721*1253*X*005010X222A1~
NM1*85*2*{context['provider']}*****XX*1234567890~
HL*1**20*1~
NM1*IL*1*DOE*JANE****MI*123456789~
SV1*HC:{bundle['cpt']}:{':'.join(bundle['modifiers'])}*...
HI*ABK:{bundle['icd'][0]}~
...~
SE*23*0001~GE*1*1~IEA*1*000000905~"""
    return {"edi": edi}
