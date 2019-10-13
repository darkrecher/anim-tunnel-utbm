unit Udescente;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls, Grids, Uremonter, ComCtrls, Spin;

type
  TRetourForm = class(TForm)
    StatisticGrid: TStringGrid;
    Retour: TButton;
    ProgressBar: TProgressBar;
    Patientez: TLabel;
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    Label4: TLabel;
    Label5: TLabel;
    Label6: TLabel;
    Label7: TLabel;
    Label8: TLabel;
    Label9: TLabel;
    Label10: TLabel;
    SpinNbrTries: TSpinEdit;
    SpinGeneLength: TSpinEdit;
    Label11: TLabel;
    Label12: TLabel;
    Label13: TLabel;
    GeneType: TLabel;
    procedure RetourClick(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure EditessaisExit(Sender: TObject);

    procedure EditsizeExit(Sender: TObject);
    procedure SpinNbrTriesExit(Sender: TObject);
    procedure SpinGeneLengthExit(Sender: TObject);



  private
    { D‚clarations priv‚es }
    NbrEssais,GeneSize:LongInt;
    ProbaCoherent:Boolean;
    PresentStats:Array[0..999] of ProbaTab;
    CumuledProba,PresentMoyenne:ProbaTab;
    {GeneSize represente la taille du gene en dinucleotide!!
  donc il faut multiplier par deux pour avoir la taille en nucleotide}
    Function StrToNucl(Nu:Char):Nucleo;
    Function Rassemble(Nu1,Nu2:Nucleo):Dinucleo;
    Function StrToDinucl(Dinu:String):Dinucleo;
    Function MakeCumuledProba(Proba:ProbaTab;var CumuProba:ProbaTab):Boolean;
    Procedure GenerateGene(var GeneChaine:String;CumuProba:ProbaTab);
    Procedure MuteGene(var GeneChaine:String;Nbr:LongInt);
    Procedure CalculProba(GeneChaine:string;var Proba:ProbaTab);
    Procedure AfficheTab(Values:ProbaTab;Col:Byte);
  public
    { D‚clarations publiques }

  end;


var
  RetourForm: TRetourForm;

implementation

{$R *.DFM}

Function TRetourForm.StrToNucl(Nu:Char):Nucleo;
begin
  Case Nu of
    'A':StrToNucl:=A;
    'C':StrToNucl:=C;
    'G':StrToNucl:=G;
    'T':StrToNucl:=T;
  end;
end;

{------------------------------------------------------------------------------}

Function TRetourForm.Rassemble(Nu1,Nu2:Nucleo):Dinucleo;
begin
  Rassemble:=Dinucleo(Ord(Nu1)*4+Ord(Nu2));
end;

{------------------------------------------------------------------------------}

Function TRetourForm.StrToDinucl(Dinu:String):Dinucleo;
begin
  if Length(Dinu)=2 then StrToDinucl:=Rassemble(StrToNucl(Dinu[1]),StrToNucl(Dinu[2]));
end;

{------------------------------------------------------------------------------}

Function TRetourForm.MakeCumuledProba(Proba:ProbaTab;var CumuProba:ProbaTab):Boolean;
var i:Byte;Somme:Real;
begin
  Somme:=0;
  For i:=0 to 15 do begin
    Somme:=Somme+Proba[i];
    CumuProba[i]:=Somme;
  end;
  MakeCumuledProba:=Abs(Somme-1)<0.00000001;
  CumuProba[15]:=1;
  //les impr‚cisions d– au calcul des probabilit‚s pass‚s font que leur somme n'est
  //pas exactement ‚gale … 1, il y a une erreur maximale de 10^-7
end;

{------------------------------------------------------------------------------}

Procedure TRetourForm.GenerateGene(var GeneChaine:String;CumuProba:ProbaTab);
Var Choice:Real;i:Byte;k:LongInt;
begin
  GeneChaine:='';
  for k:=0 to GeneSize-1 do begin
    Choice:=Random;
    i:=1;
    if Choice<=CumuProba[0] then i:=0 else While (i<=15) and
    not((Choice>CumuProba[i-1]) and (Choice<=CumuProba[i])) do Inc(i);
    GeneChaine:=GeneChaine+StrDinucleo[i];
  end;
end;

{------------------------------------------------------------------------------}

Procedure TRetourForm.MuteGene(var GeneChaine:String;Nbr:LongInt);
var i,NuclToMute:LongInt;Choice:Byte;
begin
  if Length(GeneChaine)=GeneSize*2 then for i:=0 to Nbr-1 do
  begin
    NuclToMute:=Random(GeneSize*2)+1;
    Choice:=Random(3);
    Case Choice of
      0:if GeneChaine[NuclToMute]='A' then GeneChaine[NuclToMute]:='C' else GeneChaine[NuclToMute]:='A';
      1:if (GeneChaine[NuclToMute]='C') or (GeneChaine[NuclToMute]='A')
      then GeneChaine[NuclToMute]:='G' else GeneChaine[NuclToMute]:='C';
      2:if GeneChaine[NuclToMute]='T' then GeneChaine[NuclToMute]:='G' else GeneChaine[NuclToMute]:='T';
    end;
  end;
end;

{------------------------------------------------------------------------------}

Procedure TRetourForm.CalculProba(GeneChaine:string;var Proba:ProbaTab);
var i:LongInt;DinuclToIncrease:Dinucleo;
begin
  for i:=0 to 15 do Proba[i]:=0;
  for i:=1 to GeneSize do begin
    DinuclToIncrease:=StrToDinucl(GeneChaine[i*2-1]+GeneChaine[i*2]);
    Proba[Ord(DinuclToIncrease)]:=Proba[Ord(DinuclToIncrease)]+1;
  end;
  for i:=0 to 15 do Proba[i]:=Proba[i]/GeneSize;
end;

{------------------------------------------------------------------------------}

procedure TRetourForm.FormShow(Sender: TObject);
begin
  Randomize;
  ProbaCoherent:=MakeCumuledProba(URemonter.ProbaPast,CumuledProba);
  if not(ProbaCoherent) then begin
    ShowMessage('Les probabilit‚s trouv‚s par la remont‚e analytique sont incoh‚rentes '+#13+
    'le retour simul‚ est donc impossible. Le programme va ˆtre arrˆt‚');
    Application.Terminate;
  end;
  NbrEssais:=5;
  GeneSize:=50000;
  GeneType.Caption:=NameGeneChoice;
end;

{------------------------------------------------------------------------------}

Function RealToString(X:Real):String;
var S:String;
begin
  Str(X:1:12,S);
  While S[Length(S)]='0' do Delete(S,Length(S),1);
  if (S[Length(S)]='.') or (S[Length(S)]=',') then Delete(S,Length(S),1) else
  if X=0 then S:='0';
  RealToString:=S;
end;

{------------------------------------------------------------------------------}

Procedure TRetourForm.AfficheTab(Values:ProbaTab;Col:Byte);
var i:Integer;
begin
  for i:=0 to 15 do StatisticGrid.Cells[Col,i]:=RealToString(Values[i]);
end;

{------------------------------------------------------------------------------}

Function Test(S:string;var Nbr:LongInt;Min,Max:LongInt):Boolean;
var Resu:LongInt;Error:Integer;
begin
  Val(S,Resu,Error);
  if Error=0 then if (Resu<Min) or (Resu>Max) then Error:=666;
  if Error <> 0 then ShowMessage('La valeur entr‚e n''est pas correcte.') else Nbr:=Resu;
end;

{------------------------------------------------------------------------------}

Procedure TRetourForm.EditessaisExit(Sender: TObject);
begin
{  if not(Test(EditEssais.Text,NbrEssais,1,1000)) then Text:=IntToStr(NbrEssais);}
end;

{------------------------------------------------------------------------------}

Procedure TRetourForm.EditsizeExit(Sender: TObject);
begin
 { if not(Test(Editsize.Text,GeneSize,5000,1000000000)) then Text:=IntToStr(GeneSize);}
end;

{------------------------------------------------------------------------------}

procedure TRetourForm.RetourClick(Sender: TObject);
var GeneStr:string;k:LongInt;i:Byte;Incertit,EcarType:Probatab;
begin
  AfficheTab(ProbaPast,0);
  Patientez.Visible:=True;
  Patientez.Refresh;
  ProgressBar.Visible:=True;
  ProgressBar.Max:=NbrEssais;
  ProgressBar.Position:=0;
  for k:=0 to NbrEssais-1 do begin
    GenerateGene(GeneStr,CumuledProba);
    MuteGene(GeneStr,Round(GeneSize*YMax*2));
    CalculProba(GeneStr,PresentStats[k]);
    ProgressBar.Position:=k+1;
  end;
  for i:=0 to 15 do begin
    PresentMoyenne[i]:=0;
    EcarType[i]:=0;
  end;
  for k:=0 to NbrEssais-1 do for i:=0 to 15 do PresentMoyenne[i]:=PresentMoyenne[i]+PresentStats[k][i];
  for i:=0 to 15 do PresentMoyenne[i]:=PresentMoyenne[i]/NbrEssais;
  if NbrEssais>1 then for k:=0 to NbrEssais-1 do for i:=0 to 15 do Ecartype[i]:=EcarType[i]+Sqr(PresentMoyenne[i]-PresentStats[k][i]);
  for i:=0 to 15 do Incertit[i]:=Abs(PresentMoyenne[i]-ConstPresent[i]);
  if NbrEssais>1 then for i:=0 to 15 do EcarType[i]:=Sqrt(EcarType[i]/(NbrEssais-1));
  Patientez.Visible:=False;
  ProgressBar.Visible:=False;
  AfficheTab(PresentMoyenne,1);
  if NbrEssais>1 then AfficheTab(EcarType,2);
  AffichetaB(ConstPresent,3);
  AfficheTab(Incertit,4);
end;



procedure TRetourForm.SpinNbrTriesExit(Sender: TObject);
begin
  NbrEssais:=SpinNbrTries.Value;
end;

procedure TRetourForm.SpinGeneLengthExit(Sender: TObject);
begin
  GeneSize:=SpinGeneLength.Value;
end;

end.
